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
AGENT_VERSION = AGENT_BRANCH.replace("x", "30") 


# Map of Component => Branch representing which branches of which component
# are linked to the 1.10.x branch of the agent
COMPONENT_BRANCHES = {
    "cpp-pcp-client" : (CppPcpClient, "1.5.x"),
    "pxp-agent" : (PxpAgent, "1.5.x"),
    "leatherman" : (Leatherman, "0.12.x"),
    "facter" : (Facter, "3.6.x"),
    "puppet" : (lambda *args, **kwargs: Puppet(*args, **(dict(list(kwargs.items()) + [('use_private_fork', True)]))), "4.10.x"),
    "hiera" : (Hiera, "3.3.x"),
    "marionette-collective" : (MarionetteCollective, "2.10.x"),
}

GITHUB_DIR = "%s/%s" % (os.environ['HOME'], "GitHub")
WORKSPACE = "%s/%s" % (GITHUB_DIR, "puppet-agent-workflow/workspaces/PA-1761")

def init_environment():
    # Create the agent first
    globals()['puppet_agent'] = PuppetAgent(workspace = WORKSPACE, stub_branch = identity, use_private_fork = True)
    puppet_agent.reset_branch(AGENT_BRANCH)
    puppet_agent[AGENT_BRANCH](
      rewrite_file("VERSION", AGENT_VERSION),
      commit("Rewrite the version file for the agent repo!")
    )
    puppet_agent.in_repo(sequence(
        lambda : git('push --delete origin %s' % AGENT_VERSION),
        lambda : git('tag --delete origin %s' % AGENT_VERSION),
    ))
    
    # Now create each of the components
    for component, (constructor, branch) in COMPONENT_BRANCHES.items():
        edited_name = component.replace("-", "_")
        globals()[edited_name] = constructor(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_branch = identity, update_ref = False) 
        globals()[edited_name].reset_branch(branch)
        globals()[edited_name].update_url(branch)
        prev_version = branch.replace("x", "30")
        globals()[edited_name].in_repo(sequence(
            lambda : git('push --delete origin %s' % prev_version),
            lambda : git('tag --delete origin %s' % prev_version),
        ))
        globals()[edited_name][branch](
            bump_version(prev_version)
        )
        tag_sha = globals()[edited_name].in_branch(branch, exec_stdout('git', 'rev-parse', 'HEAD')).decode("utf-8")
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
    # facter, pxp-agent, and puppet will be the ones that will be bumped
    for (component, branch) in [(facter, "3.6.x"), (puppet, "4.10.x"), (pxp_agent, "1.5.x")]:
        next_version = branch.replace("x", "31")
        component[branch](
          bump_version(next_version),
          update_ref = True
        )
        component.in_repo(sequence(
            lambda : git('push --delete origin %s' % next_version),
            lambda : git('tag --delete origin %s' % next_version),
        ))

setup_happy_cases()
puppet_agent.in_repo(sequence(
    lambda: git('branch -D %s' % AGENT_VERSION),
    lambda: git('checkout -b %s' % AGENT_VERSION),
    lambda: git('push --set-upstream origin %s --force' % AGENT_VERSION)
))
