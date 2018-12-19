from workflow.actions.file_actions import (map_lines)
from workflow.repos.git_repository import GitRepository
from workflow.repos.puppet_agent import PuppetAgent
from workflow.utils import (commit, to_action, identity, const)

import os

GITHUB_DIR = "%s/%s" % (os.environ['HOME'], "GitHub")
WORKSPACE = "%s/%s" % (GITHUB_DIR, "puppet-agent-workflow/workspaces/beaker-timing")
BRANCH_PREFIX = "beaker-timing-tests"

beaker = GitRepository("beaker", ["pa-timing"], workspace = WORKSPACE, stub_branch = identity)
beaker.reset_branch("pa-timing", remote = "origin")

puppet_agent = PuppetAgent(workspace = WORKSPACE, stub_prefix = BRANCH_PREFIX)

# Map of <repo> -> <run-beaker> script path
beaker_repos = {
    puppet_agent : "%s/%s" % (GITHUB_DIR, "scripts/puppet-agent/run-beaker.sh")
}

def link_to_local_beaker(repo, branch):
    repo.reset_branch(branch)
    repo[branch](
        map_lines("acceptance/Gemfile", r"gem ['\"]beaker['\"]", const("gem 'beaker', *location_for('file:///%s')\n" % beaker.root), 1),
        commit("Link beaker to local repo so that timing results can be printed")
    )


