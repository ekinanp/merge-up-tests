from workflow.repos.puppet_agent import *
from workflow.repos.facter import *
from workflow.constants import *

puppet_agent = PuppetAgent()
puppet_agent.reset_branches()

facter = Facter()
facter.reset_branches()

facter.bump("3.6.x", "10.12.13")
facter.reset_branches()
