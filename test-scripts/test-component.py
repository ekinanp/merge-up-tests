from workflow.component import *
from workflow.puppet_agent import *
from workflow.constants import *

puppet_agent = PuppetAgent(GITHUB_FORK, WORKSPACE)
puppet_agent.reset_branches()

component = Component(GITHUB_FORK, 'facter', WORKSPACE, {
    "3.6.x": ["1.10.x"],
    "3.9.x": ["5.3.x"],
    "master": ["master"]
})
component.reset_branches()
