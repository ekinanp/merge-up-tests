from workflow.repos.component import *
from workflow.repos.puppet_agent import *
from workflow.repos.pxp_agent import *
from workflow.repos.cpp_pcp_client import *
from workflow.constants import *
from workflow.actions.component_actions import *

puppet_agent = PuppetAgent()
puppet_agent.reset_branches()

pxp_agent = PxpAgent()
pxp_agent.reset_branch("1.8.x")


pxp_agent["1.8.x"](
    update_changelog(
        "1.8.0",
        "[PCP-790] Added support for downloading multiple tasks",
        "[#172] Fixed download errors from remote server"
    ),
    update_changelog(
        "1.8.1",
        "Just seeing if this released!",
        summary = "Some basic maintenance releases!"
    ),
    commit("Updated the CHANGELOG!")
)

cpp_pcp_client = CppPcpClient()
cpp_pcp_client.reset_branch("1.5.x")
