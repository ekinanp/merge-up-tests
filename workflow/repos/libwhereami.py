from workflow.actions.component_actions import (bump_cpp_project)
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)

class Libwhereami(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE):
        super(Libwhereami, self).__init__(
            'libwhereami',
            { "0.1.x": "5.3.x", "master": "master" },
            github_user,
            workspace
        )

    def _bump(self, branch, version):
        return bump_cpp_project("whereami", version)
