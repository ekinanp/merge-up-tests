from workflow.repos.git_repository import GitRepository
from workflow.repos.puppet_agent import PuppetAgent
from workflow.repos.hiera import Hiera
from workflow.utils import (commit, to_action, identity, const, in_directory, sequence, git_action)
from workflow.actions.repo_actions import bump_version
from workflow.actions.file_actions import (new_file, modify_line)

from jira import JIRA
import os

# The agent branch itself
AGENT_BRANCH = "5.3.x"

# Map of Component => Branch representing which branches of which component
# are linked to the 5.3.x branch of the agent
COMPONENT_BRANCHES = {
    "hiera" : (Hiera, "3.4.x")
}

GITHUB_DIR = "%s/%s" % (os.environ['HOME'], "GitHub")
WORKSPACE = "%s/%s" % (GITHUB_DIR, "puppet-agent-workflow/workspaces/PA-1768")

def add_feature(feature_name, commit_msg):
    return sequence(new_file(feature_name, "contents"), commit(commit_msg))

def reset_environment(branch_prefix):
    # Create the agent first
    globals()['puppet_agent'] = PuppetAgent(workspace = WORKSPACE, stub_branch = identity)
    puppet_agent.reset_branch(AGENT_BRANCH)

    # Now create each of the components
    for component, (constructor, branch) in COMPONENT_BRANCHES.items():
        edited_name = component.replace("-", "_")
        globals()[edited_name] = constructor(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_prefix = "PA-1768-%s" % branch_prefix, update_ref = False) 
        globals()[edited_name].reset_branch(branch)
        globals()[edited_name].update_url(branch)

    hiera["3.4.x"](
        git_action("reset --hard 74116899c41ea66da9440715cd7ea7a1dcc56cb2"),
    )

def no_code_changes_case():
    reset_environment("no-code-changes")
    no_code_change_features = ("one", "two", "three", "four")
    hiera["3.4.x"](sequence(
        *[add_feature("%s" % name, "Added no-code-change feature '%s' [no-promote]" % name) for name in no_code_change_features]
    ), add_feature("five", "Added no-code-change feature 'five'\n\nHere is the [no-promote] tag in the message body!"))

def code_changes_case():
    reset_environment("code-changes")
    hiera["3.4.x"](
        add_feature("n_one", "Added no-code-change feature one [no-promote]"),
        add_feature("one", "Added code-change feature one"),
        add_feature("n_two", "Added no-code-change feature two [no-promote]"),
        add_feature("n_three", "Added no-code-change feature two\n\nHere is the [no-promote] tag in the message body"),
    )

no_code_changes_case()
#code_changes_case()
