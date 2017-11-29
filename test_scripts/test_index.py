from workflow.repos.puppet_agent import *
from workflow.repos.facter import *
from workflow.actions.file_actions import *
from workflow.constants import *
from workflow.utils import *

from test_scripts.test_utils import WORKSPACE

puppet_agent = PuppetAgent(workspace = WORKSPACE)
puppet_agent.reset_branches()

facter = Facter(workspace = WORKSPACE, puppet_agent = puppet_agent)
facter.reset_branches()

facter['3.6.x'](
    new_file("test_file_one", "CONTENTS 1"),
    new_file("test_file_two", "CONTENTS 2"),
    commit("Testing out the new index operator!")
)
