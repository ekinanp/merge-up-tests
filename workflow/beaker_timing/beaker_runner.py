from workflow.actions.file_actions import (map_lines)
from workflow.repos.git_repository import GitRepository
from workflow.utils import (commit, to_action, identity, const, in_directory, exec_stdout)
from workflow.beaker_timing.timing_results import TimingResults

import subprocess
import os
import re
import json

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

def bundle(action):
    return os.system("BUNDLE_PATH=.bundle/gems BUNDLE_BIN=.bundle/bin bundle %s" % action)

def bundle_stdout(cmd):
    environment = os.environ.copy()
    environment["BUNDLE_PATH"] = ".bundle/gems"
    environment["BUNDLE_BIN"] = ".bundle/bin" 

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

    # This returns the host to add directly to the timing results and should also create the
    # hosts.cfg file. Child classes will need to call the parent's method at the end of their
    # implementation, as the parent will generate the ABS resources.
    # TODO: Have method return the environment! Child processes should override protected
    # method
    def setup_beaker_environment(self, host_layout):
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
        hosts_cfg = beaker_hostgenerator(host_layout)

        print("HOSTS CFG FILE:")
        print(hosts_cfg)
        print("")
        print("")
        print("ABS HOSTS: %s" % abs_hosts)
        print("TIMING TREE HOST: %s" % host)
            
        return host

    def action(self, host_layout):
        def run_beaker_action(repo_name, branch):
            map_lines("acceptance/Gemfile", r"gem ['\"]beaker['\"]", const("gem 'beaker', *location_for('file:///%s')\n" % BeakerRunner.beaker_repo.root), 1)(repo_name, branch)

            with in_directory("acceptance"):
                if not os.path.exists("beaker-results"):
                    os.makedirs("beaker-results")
                if not os.path.exists(".bundle"):
                    bundle("install")
                host = self.setup_beaker_environment(host_layout) 

#                exit_code = os.system(bundle("exec %s" % self.beaker_rake_task))
#                if exit_code != 0:
#                    Exception("beaker failed to run successfully with the host layout of %s" % host_layout)
#                TimingResults.add_host(
#                    host,
#                    "log/latest/tests-timing-trees.json",
#                    output_file = "%s/%s.json" % (BEAKER_RESULTS_DIR, host['name'])
#                )

        return run_beaker_action
