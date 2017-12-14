from workflow.actions.file_actions import (map_lines)
from workflow.repos.git_repository import GitRepository
from workflow.utils import (commit, to_action, identity, const, in_directory, exec_stdout)
from workflow.beaker_timing.timing_results import TimingResults

import subprocess
import os
import re
import json
import tempfile

# This class is a base class for "run-beaker" actions. Its constructor returns an action that
# a repo can use to run beaker tests within it. Mostly used to make the timing stuff easier.
BRANCH_PREFIX = "beaker-timing" 
WORKSPACE = "%s/beaker-timing-workspace" % os.getcwd()
BEAKER_RESULTS_DIR = "beaker-results"

VM_FLOATY_CONFIG = {
    "vm" : {
        "url"    : "https://vmpooler.delivery.puppetlabs.net/api/v1",
        "token"  : "ioxxc027rp9t0wd9zzs5jx2d3a78n8r6",
        "engine" : "vmpooler"
    },
    "ns" : {
        "url"    : "https://nspooler-service-prod-1.delivery.puppetlabs.net",
        "token"  : "289ac9a518e97b26ed17c6ed",
        "engine" : "nspooler"
    }
}

def set_bundle_environment(env_vars):
    env_vars["BUNDLE_PATH"] = ".bundle/gems"
    env_vars["BUNDLE_BIN"] = ".bundle/bin"

    return env_vars

def bundle(action, **kwargs):
    env_vars = set_bundle_environment(kwargs.get("env", {}))
    for (env_var, value) in env_vars.iteritems():
        os.putenv(env_var, value)
    return os.system("bundle %s" % action)

def bundle_stdout(cmd, **kwargs):
    environment = os.environ.copy()
    environment.update(kwargs.get("env", {}))
    environment = set_bundle_environment(environment)

    return subprocess.check_output(
        "bundle %s" % cmd,
        env = environment,
        shell = True
    )

def beaker_hostgenerator(host_layout, **kwargs):
    try:
        return bundle_stdout("exec beaker-hostgenerator %s --hypervisor abs --disable-default-role%s" % (host_layout, " --templates-only" if kwargs.get('templates_only', None) else ""))
    except subprocess.CalledProcessError as e:
        print("OUTPUT:\n%s" % e.output)
        raise e

class BeakerRunner(object):
    @classmethod
    def get_abs_host(cls, template):
        for (service, config) in VM_FLOATY_CONFIG.iteritems():
            try:
                stdout = cls.vmfloaty_repo.in_branch(
                    "master",
                    to_action(bundle_stdout)("exec floaty get %s --service %s --url %s --token %s" % (template, service, config["url"], config["token"]))
                )

                hostname = re.match(r"-\s+([^\s]+)\s+.*", stdout).group(1)

                return { "hostname" : hostname, "type" : template, "engine" : config["engine"] }
            except subprocess.CalledProcessError as e:
                pass

        raise Exception("ERROR: Could not get a VM for the template %s!" % template)

    # TODO: Move this into a metaclass or something, b/c then you need to call "get_abs_host"
    # after at least one instance is created for the class variables to be initialized.
    def __new__(cls, *args, **kwargs):
        instance = super(BeakerRunner, cls).__new__(cls, *args, **kwargs)

        const_repos = [
            ("beaker", ["pa-timing"], "ekinanp"),
            ("vmfloaty", ["master"], "ekinanp")
        ]
        for (repo_name, branches, github_user) in const_repos:
            repo_attr = "%s_repo" % repo_name
            if getattr(cls, repo_attr, None):
                continue

            repo = GitRepository(repo_name, branches, github_user, workspace = WORKSPACE, stub_branch = identity, initialize_with = lambda : bundle("install"))

            setattr(cls, repo_attr, repo)

        return instance

    def __init__(self, beaker_rake_task, tests_need_master = False):
        self.beaker_rake_task = beaker_rake_task
        self.tests_need_master = tests_need_master

    # This method should return a map of { env. var => value } representing the beaker
    # environment
    def env_vars(self, hosts_cfg_path):
        env_vars = {
            "SUITE_COMMIT" : os.environ.get("SUITE_COMMIT", "bd30b4eaa76151525a6a9af8c6d9aeee5f0f643f"),
            "SUITE_VERSION" : os.environ.get("SUITE_VERSION", "5.3.3.106.gbd30b4e"),
            "BEAKER_HOSTS" : hosts_cfg_path,
            "OPTIONS" : "--test-tag-exclude=server",
            "SERVER_VERSION" : os.environ.get("SERVER_VERSION", "latest"),
            "BEAKER_HOSTGENERATOR_VERSION": os.environ.get("BEAKER_HOSTGENERATOR_VERSION", "1")
        }
        env_vars["SHA"] = env_vars["SUITE_COMMIT"]

        return env_vars

    # Returns a triple: (hosts_cfg_path, abs_hosts, host)
    def generate_abs_hosts(self, host_layout):
        os_template = json.loads(beaker_hostgenerator(host_layout, templates_only = True)).keys()[0]
        abs_hosts = [BeakerRunner.get_abs_host(os_template)]
        host = {
            "name"     : abs_hosts[0]["hostname"],
            "platform" : abs_hosts[0]["type"]
        }

        # If test needs a master, generate one for the master as well
        if self.tests_need_master:
            master_template = json.loads(beaker_hostgenerator("redhat7-64m", templates_only = True)).keys()[0]
            abs_hosts += [BeakerRunner.get_abs_host(master_template)]
            host_layout += "-redhat7-64m"

        # Now generate the hosts.cfg file
        hosts_cfg_content = beaker_hostgenerator(host_layout)
        hosts_cfg_path = "hosts.yml"
        with open(hosts_cfg_path, "w") as f:
           f.write(hosts_cfg_content) 
            
        return (hosts_cfg_path, abs_hosts, host)

    def action(self, host_layout):
        def run_beaker_action(repo_name, branch):
            map_lines("acceptance/Gemfile", r"gem ['\"]beaker['\"]", const("gem 'beaker', *location_for('file:///%s')\n" % BeakerRunner.beaker_repo.root), 1)(repo_name, branch)

            with in_directory("acceptance"):
                if not os.path.exists("beaker-results"):
                    os.makedirs("beaker-results")
                if not os.path.exists(".bundle"):
                    bundle("install")

                hosts_cfg_path, abs_hosts, host = self.generate_abs_hosts(host_layout)
                env_vars = self.env_vars(hosts_cfg_path)
                env_vars.update({"ABS_RESOURCE_HOSTS" : json.dumps(abs_hosts, separators = (",", ":"))}) 

                exit_code = bundle("exec rake %s" % self.beaker_rake_task, env = env_vars)
                if exit_code != 0:
                    raise Exception("beaker failed to run successfully with the host layout of %s" % host_layout)
                TimingResults.add_host(
                    host,
                    "log/latest/tests-timing-trees.json",
                    output_file = "%s/%s-%s.json" % (BEAKER_RESULTS_DIR, host['name'], host['platform'])
                )

        return run_beaker_action
