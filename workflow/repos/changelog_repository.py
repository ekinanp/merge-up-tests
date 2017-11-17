from workflow.utils import (commit, const, noop_action)
from workflow.actions.component_actions import to_changelog_action
from git_repository import (GitRepository, GITHUB_FORK, WORKSPACE)

# These are GitRepositories that have a CHANGELOG
class ChangelogRepository(GitRepository):
    def __init__(self, repo_name, branches, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(ChangelogRepository, self).__init__(repo_name, branches, github_user, workspace)

        changelog_type = kwargs.get('changelog_type')
        changelog_path = kwargs.get('changelog_path')
        super(ChangelogRepository, self.__class__).changelog_info[self.name] = (changelog_type, changelog_path)

        self._init_changelog = noop_action

    def reset_branch(self, branch):
        super(ChangelogRepository, self).reset_branch(branch)

        self[branch](
            self._init_changelog,
            to_changelog_action(const(None)),
            commit("Initializing the changelog for the '%s' repo!" % self.name)
        )
