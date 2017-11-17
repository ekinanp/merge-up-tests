from workflow.actions.component_actions import (bump_cpp_project, bump_version_file, sequence)
from git_repository import (GITHUB_FORK, WORKSPACE)
from component import Component

class Facter(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(Facter, self).__init__(
            'facter',
            { "3.6.x": "1.10.x", "3.9.x": "5.3.x", "master": "master"},
            github_user,
            workspace,
            version_bumper = sequence(
                bump_cpp_project("FACTER"),
                bump_version_file("lib/Doxyfile", r'PROJECT_NUMBER\s+=\s+')
            )
        )
