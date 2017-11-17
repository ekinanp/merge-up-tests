from workflow.actions.component_actions import (bump_cpp_project, bump_version)
from workflow.utils import sequence
from git_repository import (GITHUB_FORK, WORKSPACE)
from component import Component
from workflow.actions.changelog.simple_changelog import SimpleChangelog

class Facter(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(Facter, self).__init__(
            'facter',
            { "3.6.x": "1.10.x", "3.9.x": "5.3.x", "master": "master"},
            github_user,
            workspace,
        )

    def _bump(self, branch, version):
        return sequence(
            bump_cpp_project("FACTER", version),
            bump_version("lib/Doxyfile", r'PROJECT_NUMBER\s+=\s+', version)
        )
