from workflow.actions.component_actions import bump_ruby_project
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)

class Puppet(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE):
        super(Puppet, self).__init__(
            'puppet',
            { "4.10.x": "1.10.x", "5.3.x": "5.3.x", "master": "master"},
            github_user,
            workspace
        )

    def _bump(self, branch, version):
        return bump_ruby_project(self.name, branch, version, ["5.3.x", "master"])
