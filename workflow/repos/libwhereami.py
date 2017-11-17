from workflow.actions.component_actions import bump_cpp_project
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)

class Libwhereami(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(Libwhereami, self).__init__(
            'libwhereami',
            { "0.1.x": "5.3.x", "master": "master" },
            github_user,
            workspace,
            version_bumper = bump_cpp_project("whereami") 
        )
