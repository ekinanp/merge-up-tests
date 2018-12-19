from workflow.repos.git_repository import GitRepository
from workflow.repos.puppet_agent import PuppetAgent
from workflow.repos.cpp_pcp_client import CppPcpClient
from workflow.repos.pxp_agent import PxpAgent
from workflow.repos.leatherman import Leatherman
from workflow.repos.libwhereami import Libwhereami
from workflow.repos.facter import Facter
from workflow.repos.puppet import Puppet
from workflow.repos.hiera import Hiera
from workflow.repos.marionette_collective import MarionetteCollective
from workflow.utils import (commit, to_action, identity, const, in_directory, git, git_head, sequence, exec_stdout)
from workflow.actions.repo_actions import (bump_version, bump_component)
from workflow.actions.file_actions import (new_file, modify_line, rewrite_file)

import os

# The agent branch itself
AGENT_BRANCH = "1.10.x"

# Map of Component => Branch representing which branches of which component
# are linked to the 5.3.x branch of the agent
COMPONENT_BRANCHES = {
    "cpp-pcp-client" : (CppPcpClient, "1.5.x"),
    "pxp-agent" : (PxpAgent, "1.5.x"),
    "leatherman" : (Leatherman, "0.12.x"),
    "facter" : (Facter, "3.6.x"),
    "puppet" : (Puppet, "4.10.x"),
    "hiera" : (Hiera, "3.3.x"),
    "marionette-collective" : (MarionetteCollective, "2.10.x"),
}

GITHUB_DIR = "%s/%s" % (os.environ['HOME'], "GitHub")
WORKSPACE = "%s/%s" % (GITHUB_DIR, "puppet-agent-workflow/workspaces/PA-1760")

def reset_component(component):
    branch = COMPONENT_BRANCHES[component.name][1]
    component.reset_branch(branch)
    version_to_bump = branch.replace("x", "10")
    component[branch](
        bump_version(version_to_bump),
        commit("(packaging) Bump to %s" % version_to_bump)
    )

def run_script():
    env_vars = " ".join([
        "VANAGON_REPO_BRANCH=%s" %AGENT_BRANCH,
        "VANAGON_PROJECT_NAME=puppet-agent",
        "GITHUB_USER=ekinanp",
        "VANAGON_REPO=puppet-agent",
        'COMPONENTS_TO_CHECK="%s"' % ' '.join(COMPONENT_BRANCHES.keys())
    ])

    scripts_path = "/Users/enis.inan/GitHub/ci-job-configs/resources/scripts"
    with in_directory(WORKSPACE):
        os.system("%s %s/vanagon-gather-components-to-version-bump.sh" % (env_vars, scripts_path))

def init_environment():
    # Create the agent first
    globals()['puppet_agent'] = PuppetAgent(workspace = WORKSPACE, stub_branch = identity)
    puppet_agent.reset_branch(AGENT_BRANCH)
    puppet_agent[AGENT_BRANCH](
      rewrite_file("VERSION", AGENT_BRANCH.replace("x", "30")),
      commit("Rewrite the version file for the agent repo!")
    )
    
    # Now create each of the components
    for component, (constructor, branch) in COMPONENT_BRANCHES.items():
        edited_name = component.replace("-", "_")
        globals()[edited_name] = constructor(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_branch = identity, update_ref = False) 
        globals()[edited_name].reset_branch(branch)
        globals()[edited_name].update_url(branch)
        prev_version = branch.replace("x", "30")
        next_version = branch.replace("x", "31")
        globals()[edited_name].in_repo(sequence(
            lambda : git('push --delete origin %s' % prev_version),
            lambda : git('tag --delete origin %s' % prev_version),
        ))
        globals()[edited_name][branch](
            bump_version(prev_version),
            bump_version(next_version)
        )
        tag_sha = globals()[edited_name].in_branch(branch, exec_stdout('git', 'rev-parse', 'HEAD^')).decode("utf-8")
        globals()[edited_name].in_repo(sequence(
            lambda : git('tag -a %s %s -m "Tagging to %s!"' % (prev_version, tag_sha, prev_version)),
            lambda : git('push origin --tags')
        ))
        puppet_agent[AGENT_BRANCH](
            bump_component(component, "refs/tags/%s" % prev_version),
            commit("Pinning '%s' back to previous tag!" % component)
        )

def setup_happy_cases():
    init_environment()
    # facter, pxp-agent, and puppet will be the ones that need to be bumped
    for (component, branch) in [(facter, "3.6.x"), (puppet, "4.10.x"), (pxp_agent, "1.5.x")]:
        component[branch](
            new_file("some_feature", "This is my feature"),
            commit("Created new feature to simulate a change!"),
            update_ref = True
        )

    # Note the release branch will also need to be cut at the latest sha

# facter will point to a branch, which is neither a git tag or a sha (fail)
# pxp-agent will point to its previous tag (which will be done by bumping it to version "31")
# leatherman will point to a tag that is not its previous tag
def setup_bad_ref_case():
    init_environment()
    puppet_agent[AGENT_BRANCH](
        bump_component("facter", "origin/3.6.x"),
        commit("Setting up bad ref case!")
    )

def no_version_case():
    init_environment()
    facter["3.6.x"](
        modify_line("CMakeLists.txt", r"FACTER VERSION \d.\d.\d", "FACTER VERSION bad_version"),
        commit("Put bogus version to trigger job failure")
    )

setup_happy_cases()
