from workflow.repos.puppet_agent import *
from workflow.constants import *

puppet_agent = PuppetAgent()
puppet_agent.reset_branches()

puppet_agent.bump_component("facter", "1.10.x", "foo")
