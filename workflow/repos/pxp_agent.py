from workflow.actions.repo_actions import bump_cpp_project
from workflow.actions.structured_file.simple_changelog import SimpleChangelog
from workflow.actions.file_actions import modify_lines
from git_repository import GITHUB_USERNAME
from component import Component
from changelog_repository import ChangelogRepository

class PxpAgent(Component, ChangelogRepository):
    def __init__(self, github_user = GITHUB_USERNAME, **kwargs):
        kwargs['metadata'] = {
            'changelog' : (SimpleChangelog, "CHANGELOG.md"),
            'version_bumper' : bump_cpp_project("pxp-agent")
        }

        super(PxpAgent, self).__init__(
            'pxp-agent',
            { "1.5.x": "1.10.x", "1.8.x": "5.3.x", "master": "master"},
            github_user,
            **kwargs
        )

    def _init_changelog(self):
        return modify_lines("CHANGELOG.md", "^\s+(\[[^\]]+\])", "* \g<1>")

