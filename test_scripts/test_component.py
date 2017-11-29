from workflow.repos.component import *
from workflow.repos.puppet_agent import *
from workflow.constants import *

from test_scripts.test_utils import WORKSPACE

puppet_agent = PuppetAgent(GITHUB_FORK, workspace = WORKSPACE)
puppet_agent.reset_branches()

component = Component('facter', { "3.6.x": "1.10.x", "3.9.x": "5.3.x", "master": "master" }, GITHUB_FORK, workspace = WORKSPACE)
component.reset_branches()
