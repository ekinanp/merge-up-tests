from workflow.actions.repo_actions import bump_cpp_project
from workflow.actions.structured_file.sectioned_changelog import (SectionedChangelog, update_section)
from workflow.actions.file_actions import after_line
from workflow.utils import const
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)
from changelog_repository import ChangelogRepository

class Libwhereami(Component, ChangelogRepository):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(Libwhereami, self).__init__(
            'libwhereami',
            { "0.1.x": "5.3.x", "master": "master" },
            github_user,
            workspace,
            changelog = (
                lambda contents: SectionedChangelog(contents, "Additions", "Fixes"),
                "CHANGELOG.md"
            ),
            version_bumper = bump_cpp_project("whereami") 
        )

    def _init_changelog(self):
        return after_line("CHANGELOG.md", "Initial release of", const("\n### Additions"))

additions = update_section("Additions")
fixes = update_section("Fixes")
