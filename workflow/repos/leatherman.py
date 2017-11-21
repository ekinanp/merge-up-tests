from workflow.actions.repo_actions import bump_cpp_project
from workflow.actions.structured_file.sectioned_changelog import (SectionedChangelog, update_section)
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)
from changelog_repository import ChangelogRepository

class Leatherman(Component, ChangelogRepository):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(Leatherman, self).__init__(
            'leatherman',
            { "0.12.x": "1.10.x", "1.2.x": "5.3.x", "master": "master"},
            github_user,
            workspace,
            changelog = (
                lambda contents: SectionedChangelog(contents, "Added", "Fixed", "Changed", "Known Issues", "Removed"),
                "CHANGELOG.md"
            ),
            version_bumper = bump_cpp_project('leatherman')
        )

added = update_section("Added")
fixed = update_section("Fixed")
changed = update_section("Changed")
known_issues = update_section("Known Issues")
removed = update_section("Removed")
