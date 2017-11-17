from workflow.actions.component_actions import bump_ruby_project
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)

class Hiera(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(Hiera, self).__init__(
            'hiera',
            { "3.3.x": "1.10.x", "3.4.x": "5.3.x", "master": "master"},
            github_user,
            workspace,
            version_bumper = bump_ruby_project('hiera', ["3.4.x", "master"])
        )
