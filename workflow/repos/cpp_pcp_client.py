from workflow.actions.component_actions import bump_cpp_project
from component import Component
from workflow.actions.changelog.simple_changelog import SimpleChangelog
from git_repository import (GITHUB_FORK, WORKSPACE)
from component import Component
from changelog_repository import ChangelogRepository

class CppPcpClient(Component, ChangelogRepository):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE):
        super(CppPcpClient, self).__init__(
            'cpp-pcp-client',
            { "1.5.x": ["1.10.x", "5.3.x"], "master": "master"},
            github_user,
            workspace,
            changelog = (SimpleChangelog, "CHANGELOG.md"),
            version_bumper = bump_cpp_project('cpp-pcp-client')
        )
