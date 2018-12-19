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
AGENT_BRANCH = "5.3.x"
RELEASE_BRANCH = AGENT_BRANCH.replace("x", "50") + "-release"

GITHUB_DIR = "%s/%s" % (os.environ['HOME'], "GitHub")
WORKSPACE = "%s/%s" % (GITHUB_DIR, "puppet-agent-workflow/workspaces/PA-1762")

# Create the agent first
globals()['puppet_agent'] = PuppetAgent(workspace = WORKSPACE, stub_branch = identity, use_private_fork = True)
puppet_agent.reset_branch(AGENT_BRANCH)
puppet_agent.in_repo(sequence(
    lambda: git('branch -D %s' % RELEASE_BRANCH),
    lambda: git('checkout -b %s' % RELEASE_BRANCH),
    lambda: git('push --set-upstream origin %s --force' % RELEASE_BRANCH)
))

puppet_agent.in_repo(sequence(
    lambda: new_file("feature_one", "first feature")("", ""),
    lambda: new_file("feature_two", "second feature")("", ""),
    lambda: commit("Added some features to set-up stuff to merge-up")("", ""),
    lambda: git("push")
))
