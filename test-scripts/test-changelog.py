from workflow.repos.component import *
from workflow.repos.puppet_agent import *
from workflow.repos.pxp_agent import *
from workflow.repos.cpp_pcp_client import *
from workflow.repos.leatherman import *
from workflow.repos.libwhereami import *
from workflow.constants import *
from workflow.actions.repo_actions import *

def test_simple_changelog():
    puppet_agent = PuppetAgent()
    puppet_agent.reset_branches()

    for (component_type, branch) in [(PxpAgent, "1.8.x"), (CppPcpClient, "1.5.x")]:
        component = component_type() 
        component.reset_branch(branch)
        component[branch](
            update_changelog(
                "1.8.0",
                "[PCP-790] Added support for downloading multiple tasks",
                "[#172] Fixed download errors from remote server",
                "[PCP-1231] Hope this works!",
                summary = "Some random stuff!"
            ),
            update_changelog(
                "1.8.1",
                "Just seeing if this released!",
                summary = "Some basic maintenance releases!"
            ),
            update_changelog(
                "1.2.10",
                "Seeing if versions maintain sorted order!",
                summary = "Premature releases!"
            ),
            update_changelog(
                "1.2.10",
                "Some random update!",
            ),
            commit("Updated the CHANGELOG!")
        )

def test_sectioned_changelog():
    puppet_agent = PuppetAgent()
    puppet_agent.reset_branches()

    # Test out Leatherman
    leatherman = Leatherman()
    leatherman.reset_branch("master")
    leatherman["master"](
        update_changelog(
            "1.3.1",
            fixed(
                "Task download erroring on a 500",
                "Leatherman.curl to give better exception clarity"
            ),
            added(
                "New feature to hack into everything"
            ),
            changed("Lots of stuff changed!")
        ),
        update_changelog(
            "1.1.1",
            fixed(
                "Testing if it can insert into an existing version"
            )
        ),
        update_changelog(
            "1.1.0",
            changed("Seeing if a new section is inserted into an existing version!")
        ),
        commit("Updated the CHANGELOG!")
    )

    # libwhereami test is just to make sure its specific routines work,
    # all the correctness stuff was tested with leatherman above
    libwhereami = Libwhereami()
    libwhereami.reset_branch("master")
    libwhereami["master"](
        update_changelog(
            "1.3.1",
            additions("Stuff!"),
            fixes("Lots of stuff!")
        ),
        commit("Updated the CHANGELOG!")
    )

#test_simple_changelog()
test_sectioned_changelog()
