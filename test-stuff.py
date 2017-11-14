from workflow.file_actions import *
from workflow.git_repository import *
from workflow.constants import *

commit = GitRepository.commit

facter = GitRepository(GITHUB_FORK, "facter", WORKSPACE, ["3.6.x", "3.9.x", "master"])
facter.reset_branches()

facter.in_branch(
    "3.6.x",
    update_file("CMakeLists.txt", lambda f: f.write("appending stuff")),
    create_file("some_feature", lambda f: f.write("some feature")),
    remove_file("locales/FACTER.pot"),
    commit("Testing out some CRUD stuff!")
)
