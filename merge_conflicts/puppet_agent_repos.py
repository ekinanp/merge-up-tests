import re

from workflow.repos.puppet_agent import PuppetAgent
from workflow.repos.cpp_pcp_client import CppPcpClient
from workflow.repos.facter import Facter
from workflow.repos.hiera import Hiera
from workflow.repos.leatherman import Leatherman
from workflow.repos.libwhereami import Libwhereami
from workflow.repos.marionette_collective import MarionetteCollective
from workflow.repos.puppet import Puppet
from workflow.repos.pxp_agent import PxpAgent

# NOTE: Should set a workspace here as well

PUPPET_AGENT = PuppetAgent()
COMPONENTS = {
    'cpp-pcp-client': CppPcpClient(puppet_agent = PUPPET_AGENT),
    'facter': Facter(puppet_agent = PUPPET_AGENT),
    'hiera': Hiera(puppet_agent = PUPPET_AGENT),
    'leatherman': Leatherman(puppet_agent = PUPPET_AGENT),
    'libwhereami': Libwhereami(puppet_agent = PUPPET_AGENT),
    'marionette-collective': MarionetteCollective(puppet_agent = PUPPET_AGENT),
    'puppet': Puppet(puppet_agent = PUPPET_AGENT),
    'pxp-agent': PxpAgent(puppet_agent = PUPPET_AGENT),
}
GLOBAL_NAMES = {
    'marionette-collective': 'MCOLLECTIVE'
}

# python hack to dynamically define variables
for component in COMPONENTS:
    global_name = GLOBAL_NAMES.get(component, re.sub("-", "_", component.upper()))
    globals()[global_name] = COMPONENTS[component]
