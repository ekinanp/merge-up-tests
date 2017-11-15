from workflow.actions.component_actions import (bump_cpp_project)
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)

class PxpAgent(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE):
        super(PxpAgent, self).__init__(
            'pxp-agent',
            { "1.5.x": "1.10.x", "1.8.x": "5.3.x", "master": "master"},
            github_user,
            workspace
        )

    def _bump(self, branch, version):
        return bump_cpp_project(self.name, version)
