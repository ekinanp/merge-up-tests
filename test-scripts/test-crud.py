from workflow.actions.file_actions import *
from workflow.repos.git_repository import *
from workflow.constants import *
from workflow.utils import commit

facter = GitRepository("facter", ["3.6.x", "3.9.x", "master"])
facter.reset_branches()

facter.to_branch(
    "3.6.x",
    new_file("my_test_file", "1234\nIS\nNOT GOOD\nFOO"),
    modify_line("my_test_file", r"(\d*)", r"NUMBER: \g<1>"),
    remove_file("CMakeLists.txt"),
    rewrite_file("MAINTAINERS", "NO MAN"),
    new_file("test_after", "Line One\nLine Two\nLine Three"),
    after_lines("test_after", "Line", "Some junk right below!"),
    new_file("test_before", "Line One\nLine Two\nLine Three"),
    before_lines("test_before", "Line", "Some junk right before!"),
    commit("Testing out some CRUD stuff!")
)

contents = facter.in_branch(
    "3.6.x",
    read_file("CONTRIBUTING.md")
)

print("CONTRIBUTING CONTENTS:")
print(contents)
