import workflow.repos.constants

from workflow.repos.constants import (REPOS, workspace)
from workflow.actions.repo_actions import (bump_version, bump_component, read_version)
from workflow.actions.file_actions import (new_file, read_file)
from workflow.utils import (identity, exec_stdout, git_action, git_head, push, sequence, commit, in_directory, noop_action)

from jira import JIRA
from functools import cmp_to_key
import os
import re
import json
import uuid

WORKSPACE = workspace("PA-1759")

def pa_components():
    return workflow.repos.constants.pa_components("master")

def var_name(repo_name):
    return repo_name.replace("-", "_")


def cmd(cmd, **kwargs):
    return lambda : subprocess.check_output(cmd.split(" "), **kwargs).decode("utf-8").strip()

def parse_xy(maint_branch):
    return tuple(map(int, maint_branch.split('.')[:-1]))

def to_fix_version(maint_branch):
    return '.'.join(map(str, parse_xy(maint_branch) + (30,)))

def strip_prefix(prefix, branch):
    return branch[len(prefix):]

def delete_tag(tag):
    return sequence(
        git_action('tag -d %s' % tag),
        git_action('push origin :refs/tags/%s' % tag)
    )

def create_commit(msg):
    return sequence(
        new_file(uuid.uuid4().hex, "new temporary file"),
        commit(msg)
    )

def no_promote(msg):
    return create_commit(msg + " [no-promote]")

def code_change(msg):
    return create_commit(msg)

def n_times(commit_action, n):
    return sequence(
        *[commit_action("%s" % i) for i in  range(1, n+1)]
    )

def latest_maint_branch(repo):
    stdout = repo.in_branch("master", exec_stdout("git", "ls-remote", "--heads", "origin")).split("\n")
    maint_branches = []
    for line in stdout:
        _, branch = line.split()
        branch = strip_prefix("refs/heads/", branch)
        if re.match('^[0-9]+\.[0-9]+\.[xz]$', branch):
            maint_branches.append(branch)

    sorted_maint_branches = sorted(maint_branches, key = parse_xy)
    return sorted_maint_branches[-1]

def to_maint_branch(version):
    return '.'.join(version.split('.')[:-1] + ['x'])

def merge(from_branch):
    return git_action("merge %s --no-edit --strategy ours" % from_branch)

def revert_new_maint_branch(repo):
    repo.reset_branch("master")
    master_version = repo.in_branch("master", read_version)
    maint_branch = to_maint_branch(master_version)
    repo.in_branch("master",
        sequence(
            git_action("branch -D %s" % maint_branch),
            git_action("push origin --delete %s" % maint_branch)
        )
    )

# This routine does the following things:
#   - Resets the component's master branch, and then deletes any new maint
#   branches that might have been cut from a previous run
#   - Creates a "code change" commit in master. See below for why.
#   - Resets the latest maint branch of component to the master in (a)
#   Note that this latest maint branch will contain the code change created
#   in master. Idea is to ensure that the maint branch automation starts
#   checking commits that come AFTER the merge_base. I.e., we create a 'code-change'
#   merge_base.
#   - Updates component's version file to some pre-specified Z version
#   - Tags the component at the pre-specified version specified
#   - Pins the component json of the corresponding agent branch to the tag
#   created above
#
# Pre-conditions:
#   (1) The component's agent repo should have been resetted.
#
# NOTE: If resetting after a test run, ensure that any "created" maint branches
# are deleted. How do we detect these? Will still need a version-file reader
# here.
def reset_component(component_repo):
    revert_new_maint_branch(component_repo)
    component_repo.update_url("master")
    component_repo["master"](
        code_change("Creating a 'code-change' merge-base!")
    )

    latest = latest_maint_branch(component_repo) 
    fix_version = to_fix_version(latest)
    component_repo[latest](
        git_action("reset --hard refs/heads/master"),
        bump_version(fix_version)
    )
    component_repo.update_url(latest)

    component_repo.in_branch(latest,
        sequence(
            delete_tag(fix_version),
            git_action("tag -a %s -m 'Setting up a z-release tag!'" % fix_version),
            push('--tags --force')
        )
    )
   
    # Push all changes made to the component to origin
    component_repo[latest](noop_action, push = True)
    component_repo["master"](noop_action, push = True)

    agent_repo = component_repo.puppet_agent
    latest = latest_maint_branch(agent_repo)
    agent_repo[latest](
        bump_component(component_repo.component_name, "refs/tags/%s" % fix_version),
        commit("Pinning %s to the tag %s!" % (component_repo.component_name, fix_version)),
    )

# Returns a map:
#  (1) 'latest_maint_branch' => (<new>, <branch>)
#  (2) 'master_head'         => <sha>
#  (3) 'ref_in_agent_master' => <ref>
def get_component_data(component):
    latest_branch = latest_maint_branch(component)
    master_version = component.in_branch("master", read_version)
    x_master, y_master = parse_xy(master_version)
    x_latest, y_latest = parse_xy(latest_branch)
    is_new_maint_branch = x_master == x_latest and y_master == y_latest
    maint_branch = (is_new_maint_branch, latest_branch)

    master_head = component.in_branch("master", git_head)

    component_json_master = json.loads(component.puppet_agent.in_branch(
        "master",
        read_file("configs/components/%s.json" % component.component_name)
    ))
    ref_in_agent_master = component_json_master["ref"]

    return {
        'latest_maint_branch' : maint_branch,
        'master_head'         : master_head[:11],
        'ref_in_agent_master' : ref_in_agent_master[:11]
    }

def print_component_data():
    component_data = {}
    for component in set(REPOS.keys()) - set(['puppet-agent']):
        component_repo = globals()[var_name(component)]
        component_data[component] = get_component_data(component_repo)

    print("\n\n\n")
    print("COMPONENT%sLATEST MAINT%sMASTER HEAD%sREF IN AGENT MASTER" % (" " * 8, " " * 5, " " * 5))
    for component in set(REPOS.keys()) - set(['puppet-agent']):
        print("%s     %s     %s     %s" % (
            component,
            component_data[component]['latest_maint_branch'],
            component_data[component]['master_head'],
            component_data[component]['ref_in_agent_master'],
        ))
        print("")

# Initializing global variables
puppet_agent = REPOS['puppet-agent'](workspace = WORKSPACE, stub_branch = identity)
for component in set(REPOS.keys()) - set(['puppet-agent']):
    globals()[var_name(component)] = REPOS[component](puppet_agent = puppet_agent, update_ref = True, workspace = WORKSPACE, stub_branch = identity)

# Function to reset the test environment to a clean slate
def reset_test_environment():
    revert_new_maint_branch(puppet_agent)
    puppet_agent.reset_branch(latest_maint_branch(puppet_agent))
    for component in pa_components():
        reset_component(globals()[var_name(component)])

    # Push changes made to the agent
    latest = latest_maint_branch(puppet_agent)
    puppet_agent[latest](noop_action, push = True)
    puppet_agent["master"](noop_action, push = True)

def build_ci_utils_gem():
    with in_directory("/Users/enis.inan/GitHub/platform-ci-utils"):
        os.system("./install-local-gem.sh")

# Displays the command to invoke the right task for platform-ci-utils
# to run the test maint branch task
def get_run_command():
    env_vars = {}
    env_vars['VANAGON_REPO'] = 'puppet-agent'
    env_vars['COMPONENTS_TO_CHECK'] = (' '.join(pa_components())).join(['"', '"'])
    env_str = ' '.join([
        "%s=%s" % (env_var, value) for env_var, value in env_vars.items()
    ])

    return "%s platform-ci-utils pa-cut-maint-branches --ssh-public-key=/Users/enis.inan/.ssh/id_rsa.pub --ssh-private-key=/Users/enis.inan/.ssh/id_rsa" % env_str

def setup_gem():
    build_ci_utils_gem()
    print("RUN COMMAND:\n  %s" % get_run_command())

# Happy case is when the following components will contain code changes:
#   - puppet
#   - pxp-agent
# For simplicity, the code-changes will be pretty much the same. (This is 
# also to make sure the right maint branches are cut)
#
# The following components will have only no-promote commits. There will be some
# "merge-ups" in there to ensure that the right merge-base is chosen.
#   - facter
def setup_happy_case():
    reset_test_environment()

    ## COMPONENTS WITH CODE CHANGES
    for component in [puppet, pxp_agent]:
        latest = latest_maint_branch(component) 
        # Introduce a few code-changes in the latest maint
        component[latest](
            n_times(code_change, 3),
            push = True
        )

        # Some no-promote commits, and then a few code-changes in master
        component["master"](
            no_promote("1"),
            no_promote("2"),
            n_times(code_change, 2)
        )

        # Merge-up latest with master.
        component["master"](
            merge(latest),
            push = True
        )

    ## COMPONENTS WITHOUT CODE CHANGES
    for component in [facter]:
        latest = latest_maint_branch(component) 
        # Introduce a few code-changes in the latest maint
        component[latest](
            n_times(code_change, 2),
            push = True
        )

        component["master"](
            n_times(no_promote, 2)
        )

        # Merge-up latest with master.
        component["master"](
            merge(latest),
            push = True
        )

    ## Push the changes up to the agent
    latest = latest_maint_branch(puppet_agent)
    puppet_agent[latest](noop_action, push = True)
    puppet_agent["master"](noop_action, push = True)

def setup_real_world():
    revert_new_maint_branch(puppet_agent)
    puppet_agent.reset_branches(push = True)

    for repo in pa_components():
        repo_obj = globals()[var_name(repo)]
        repo_obj.update_ref = False

        revert_new_maint_branch(repo_obj)
        repo_obj.reset_branches(push = True)

## CODE STARTS HERE

#setup_happy_case()
#setup_real_world()
#print_component_data()
#setup_gem()

