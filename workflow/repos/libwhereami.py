from workflow.actions.repo_actions import bump_cpp_project
from workflow.actions.structured_file.sectioned_changelog import (SectionedChangelog, update_section)
from workflow.actions.file_actions import after_line
from workflow.utils import (const, noop_action)
from component import Component
from git_repository import GITHUB_USERNAME
from changelog_repository import ChangelogRepository

class Libwhereami(Component, ChangelogRepository):
    def __init__(self, github_user = GITHUB_USERNAME, **kwargs):
        kwargs['metadata'] = {
            'changelog' : (
                lambda contents: SectionedChangelog(contents, "Summary", "Features", "Additions", "Fixes"),
                "CHANGELOG.md"
            ),
            'version_bumper' : bump_cpp_project("whereami") 
        }

        super(Libwhereami, self).__init__(
            'libwhereami',
            { "0.1.x": "5.3.x", "master": "master" },
            github_user,
            **kwargs
        )

    def _init_changelog(self):
        def init_changelog_action(repo, branch):
            return after_line("CHANGELOG.md", "Initial release of", const("\n### Additions"))(repo, branch) if branch != "0.1.x" else noop_action(repo, branch) 

        return init_changelog_action

additions = update_section("Additions")
fixes = update_section("Fixes")
