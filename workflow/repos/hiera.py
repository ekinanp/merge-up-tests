from workflow.actions.component_actions import bump_ruby_project
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)

class Hiera(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE):
        super(Hiera, self).__init__(
            'hiera',
            { "3.3.x": "1.10.x", "3.4.x": "5.3.x", "master": "master"},
            github_user,
            workspace,
        )

    def _bump(self, branch, version):
        return bump_ruby_project(self.name, branch, version, ["3.4.x", "master"])
