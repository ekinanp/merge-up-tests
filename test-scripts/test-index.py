from workflow.repos.puppet_agent import *
from workflow.repos.facter import *
from workflow.actions.file_actions import *
from workflow.constants import *
from workflow.utils import *

puppet_agent = PuppetAgent()
puppet_agent.reset_branches()

facter = Facter()
facter.reset_branches()

facter['3.6.x'](
    new_file("test_file_one", "CONTENTS 1"),
    new_file("test_file_two", "CONTENTS 2"),
    commit("Testing out the new index operator!")
)
