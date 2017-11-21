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

PUPPET_AGENT = PuppetAgent()
COMPONENTS = {
    'cpp-pcp-client': CppPcpClient(),
    'facter': Facter(),
    'hiera': Hiera(),
    'leatherman': Leatherman(),
    'libwhereami': Libwhereami(),
    'marionette-collective': MarionetteCollective(),
    'puppet': Puppet(),
    'pxp-agent': PxpAgent(),
}
GLOBAL_NAMES = {
    'marionette-collective': 'MCOLLECTIVE'
}

# python hack to dynamically define variables
for component in COMPONENTS:
    global_name = GLOBAL_NAMES.get(component, re.sub("-", "_", component.upper()))
    globals()[global_name] = COMPONENTS[component]
