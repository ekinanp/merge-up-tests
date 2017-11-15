from component_actions import (bump_cpp_project)
from component import Component

class Libwhereami(Component):
    def __init__(self, github_user, workspace):
        super(Libwhereami, self).__init__(
            github_user,
            'libwhereami',
            workspace,
            { "0.1.x": "5.3.x", "master": "master" }
        )

    def _bump(self, branch, version):
        return bump_cpp_project("whereami", version)
