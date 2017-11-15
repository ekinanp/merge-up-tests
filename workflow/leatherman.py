from component_actions import (bump_cpp_project)
from component import Component

class Leatherman(Component):
    def __init__(self, github_user, workspace):
        super(Leatherman, self).__init__(
            github_user,
            'leatherman',
            workspace,
            { "0.12.x": "1.10.x", "1.2.x": "5.3.x", "master": "master"}
        )

    def _bump(self, branch, version):
        return bump_cpp_project(self.name, version)
