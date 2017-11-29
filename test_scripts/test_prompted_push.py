from workflow.actions.file_actions import *
from workflow.repos.git_repository import *
from workflow.constants import *
from workflow.utils import (commit, const)

from test_scripts.test_utils import WORKSPACE

facter = GitRepository("facter", ["3.6.x", "3.9.x", "master"], workspace = WORKSPACE)
facter.reset_branch("3.6.x")

facter.to_branch(
    "3.6.x",
    new_file("Prompted_Push", "Prompting the git push!"),
    commit("Testing out the prompted push!"),
    prompt_push = True
)
