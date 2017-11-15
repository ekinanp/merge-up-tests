from component_actions import (bump_cpp_project)
from file_actions import replace_line
from utils import sequence
from component import Component
from constants import VERSION_RE

class Facter(Component):
    def __init__(self, github_user, workspace):
        super(Facter, self).__init__(
            github_user,
            'facter',
            workspace,
            { "3.6.x": ["1.10.x"], "3.9.x": ["5.3.x"], "master": ["master"]}
        )

    def _bump(self, branch, version):
        return sequence(
            bump_cpp_project("FACTER", version),
            replace_line(
              "lib/Doxyfile",
              r"(PROJECT_NUMBER\s+=\s+)%s" % VERSION_RE,
              "\g<1>%s" % version
            )
        )
