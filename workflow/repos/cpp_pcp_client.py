from workflow.actions.repo_actions import bump_cpp_project
from component import Component
from workflow.actions.structured_file.simple_changelog import SimpleChangelog
from git_repository import GITHUB_USERNAME
from component import Component
from changelog_repository import ChangelogRepository

class CppPcpClient(Component):
    def __init__(self, github_user = GITHUB_USERNAME, **kwargs):
        kwargs['metadata'] = {
            'changelog' : (SimpleChangelog, "CHANGELOG.md"),
            'version_bumper' : bump_cpp_project('cpp-pcp-client')
        }

        super(CppPcpClient, self).__init__(
            'cpp-pcp-client',
            { "1.5.x": ["1.10.x", "5.3.x"], "master": "master"},
            github_user,
            **kwargs
        )
