from component_actions import (bump_cpp_project)
from component import Component

class PxpAgent(Component):
    def __init__(self, github_user, workspace):
        super(PxpAgent, self).__init__(
            github_user,
            'pxp-agent',
            workspace,
            { "1.5.x": ["1.10.x"], "1.8.x": ["5.3.x"], "master": ["master"]}
        )

    def _bump(self, branch, version):
        return bump_cpp_project(self.name, version)
