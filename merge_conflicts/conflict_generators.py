from workflow.actions.repo_actions import (bump_component, bump_version, update_changelog)
from workflow.actions.file_actions import modify_line
from workflow.utils import (sequence, exec_stdout, commit, git_head, git_action)
from workflow.repos.leatherman import *
from merge_conflicts.puppet_agent_repos import *

# this routine will return the stdout of running the merge command.
# it will list any conflicts if they appear
def merge(repo, from_branch, to_branch):
    sha = repo.in_branch(from_branch, git_head)
    repo.in_branch(
        to_branch,
        git_action("merge %s --no-edit --no-ff" % sha)
    )

def component_json_conflict(from_branch, to_branch):
    refs = {
        from_branch: "foo",
        to_branch: "bar"
    }
    components = [component for component in COMPONENTS.keys() if component != "libwhereami"]

    for branch in refs:
        PUPPET_AGENT[branch](
            sequence(*[bump_component(component, refs[branch]) for component in components]),
            commit("Creating a bunch of component.json merge conflicts!")
        )

def version_bump_conflict(repo, from_branch, to_branch):
    repo[from_branch](bump_version("10.12.3"))
    repo[to_branch](bump_version("11.15.7"))

# this is when we have areas with duplicate entries
def leatherman_changelog_conflict():
    LEATHERMAN["0.12.x"](
        update_changelog(
            "0.12.2",
            fixed(
                "Bunch of random stuff that keeps failing",
                "More random stuff that keeps failing"
            )
        ),
        commit("Creating a CHANGELOG conflict!")
    )

    LEATHERMAN["1.2.x"](
        update_changelog(
            "1.2.3",
            fixed(
                "Nothing. This is just to make a conflict"
            ),
            added(
                "Bunch of cool new API features.",
                "More random stuff that will not be used"
            )
        ),
        commit("Creating a CHANGELOG conflict!")
    )

# just using pxp-agent for now, can also include other repos when
# necessary
def pot_file_metadata_conflict():
    PXP_AGENT["1.8.x"](
        modify_line("locales/pxp-agent.pot", r'POT-Creation-Date: [^"]*', r"POT-Creation-Date: 2017-10-25 23:09+0000\\n"),
        commit("Creating a POT file conflict!")
    )

    PXP_AGENT["master"](
        modify_line("locales/pxp-agent.pot", r'POT-Creation-Date: [^"]*', r"POT-Creation-Date: 2017-09-26 17:02+0000\\n"),
        commit("Creating a POT file conflict!")
    )
