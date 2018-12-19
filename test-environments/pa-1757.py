from workflow.repos.constants import (REPOS, workspace)
from workflow.actions.repo_actions import (bump_version)
from workflow.utils import (commit, to_action, identity, const, in_directory, sequence, git)
from workflow.actions.file_actions import (new_file, modify_line)

from jira import JIRA
import os

# The agent branch itself
AGENT_BRANCH = "master"

# Map of Component => Branch representing which branches of which component
# are linked to the 5.3.x branch of the agent
COMPONENT_BRANCHES = {
    "leatherman" : "master",
    "facter" : "master",
}

GITHUB_DIR = "%s/%s" % (os.environ['HOME'], "GitHub")
WORKSPACE = "%s/%s" % (GITHUB_DIR, "puppet-agent-workflow/workspaces/PA-1757")
BRANCH_PREFIX = "PA-1757"

jira = JIRA(server=os.environ['JIRA_INSTANCE'], basic_auth=(os.environ['JIRA_USER'], os.environ['JIRA_PASSWORD']))

def create_jira_ticket(project, summary):
    return jira.create_issue(project = project, summary = summary, issuetype = { 'name': 'Bug' })

def add_feature(feature_name, commit_msg):
    return sequence(new_file(feature_name, "contents"), commit(commit_msg))

def reset_environment():
    # Create the agent first
    globals()['puppet_agent'] = REPOS['puppet-agent'](workspace = WORKSPACE, stub_branch = identity)
    puppet_agent.reset_branch(AGENT_BRANCH, push = True)

    # Now create each of the components
    for component, branch in COMPONENT_BRANCHES.items():
        edited_name = component.replace("-", "_")
        globals()[edited_name] = REPOS[component](workspace = WORKSPACE, puppet_agent = puppet_agent, stub_branch = identity, update_ref = True) 
        globals()[edited_name].reset_branch(branch, push = True)

def simulate_workflow(repo, last_passing_ref, project):
    ticket_summaries = [
        "Add component A",
        "Add component B",
        "Add component C"
    ]

    issues = [create_jira_ticket(project, summary).key for summary in ticket_summaries]
    repo.in_repo(
        lambda : git("reset --hard %s" % last_passing_ref)
    )
    if repo != puppet_agent:
        repo.update_url(COMPONENT_BRANCHES[repo.name])

    repo["master"](
        add_feature("maint_one", "(maint) Added maint_one"),
        add_feature("one_one", "(%s) Added one_one feature" % issues[0]),
        add_feature("two_one", "(%s) Added two_one feature" % issues[1]),
        add_feature("one_two", "(%s) Added one_two feature" % issues[0]),
        add_feature("one_three", "(%s) Added one_three feature" % issues[0]),
        add_feature("two_two", "(%s) Added two_two feature" % issues[1]),
        add_feature("packaging", "(packaging) Committed some packaging work"),
        add_feature("no_label", "Committed some non-label work"),
        add_feature("three_one", "(%s) Added three_one feature" % issues[2]),
        push = True,
        push_agent = True,
    )

reset_environment()
simulate_workflow(puppet_agent, "1b72838297e3d0d68ba96ecd2caaee74144c16e8", "PA")
simulate_workflow(facter, "bd10437ac34c9e32acbc1f1cb00205f4c6b3e736", "FACT")
simulate_workflow(leatherman, "4974b3f33dd9087db010f0d9d7e6a45f8a116624", "LTH")
