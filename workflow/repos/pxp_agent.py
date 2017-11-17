from workflow.actions.component_actions import (bump_cpp_project)
from workflow.actions.changelog.simple_changelog import SimpleChangelog
from workflow.actions.file_actions import modify_lines
from git_repository import (GITHUB_FORK, WORKSPACE)
from component import Component
from changelog_repository import ChangelogRepository

class PxpAgent(Component, ChangelogRepository):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(PxpAgent, self).__init__(
            'pxp-agent',
            { "1.5.x": "1.10.x", "1.8.x": "5.3.x", "master": "master"},
            github_user,
            workspace,
            changelog_type = SimpleChangelog,
            changelog_path = "CHANGELOG.md",
        )

        self._init_changelog = modify_lines("CHANGELOG.md", "^\s+(\[[^\]]+\])", "* \g<1>")

    def _bump(self, branch, version):
        return bump_cpp_project(self.name, version)
