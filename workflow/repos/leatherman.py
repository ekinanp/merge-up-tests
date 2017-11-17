from workflow.actions.repo_actions import bump_cpp_project
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)

class Leatherman(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(Leatherman, self).__init__(
            'leatherman',
            { "0.12.x": "1.10.x", "1.2.x": "5.3.x", "master": "master"},
            github_user,
            workspace,
            version_bumper = bump_cpp_project('leatherman')
        )