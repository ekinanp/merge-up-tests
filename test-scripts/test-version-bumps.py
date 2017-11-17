from workflow.repos.puppet_agent import *
from workflow.repos.cpp_pcp_client import *
from workflow.repos.facter import *
from workflow.repos.hiera import *
from workflow.repos.leatherman import *
from workflow.repos.libwhereami import *
from workflow.repos.marionette_collective import *
from workflow.repos.puppet import *
from workflow.repos.pxp_agent import *
from workflow.constants import *
from workflow.actions.repo_actions import *

def test_version_bump(component_type, *branches):
    puppet_agent = PuppetAgent()
    puppet_agent.reset_branches()

    component = component_type() 
    for branch in branches:
        component.reset_branch(branch)
        component[branch](bump_version("10.12.13"))

components = [
    (CppPcpClient, "1.5.x"),
    (Facter, "3.6.x"),
    (Hiera, "3.3.x", "3.4.x"),
    (Leatherman, "0.12.x"),
    (Libwhereami, "master"),
    (MarionetteCollective, "2.11.x"),
    (Puppet, "4.10.x", "5.3.x"),
    (PxpAgent, "1.8.x"),
]

for component in components:
    test_version_bump(component[0], *component[1:])
