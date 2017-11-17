from workflow.repos.component import *
from workflow.repos.puppet_agent import *
from workflow.repos.pxp_agent import *
from workflow.repos.cpp_pcp_client import *
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
                summary = "Some random stuff!"
            ),
            update_changelog(
                "1.8.1",
                "Just seeing if this released!",
                summary = "Some basic maintenance releases!"
            ),
            commit("Updated the CHANGELOG!")
        )

test_simple_changelog()
