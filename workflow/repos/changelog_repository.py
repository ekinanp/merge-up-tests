from workflow.utils import (commit, const, noop_action)
from workflow.actions.repo_actions import to_changelog_action
from git_repository import (GitRepository, GITHUB_FORK)

# These are GitRepositories that have a CHANGELOG
class ChangelogRepository(GitRepository):
    def __init__(self, repo_name, branches, github_user = GITHUB_FORK, **kwargs):
        super(ChangelogRepository, self).__init__(repo_name, branches, github_user, **kwargs)

    def _init_changelog(self):
        return noop_action
 
    def reset_branch(self, branch):
        super(ChangelogRepository, self).reset_branch(branch)

        self[branch](
            self._init_changelog(),
            to_changelog_action(const(None)),
            commit("Initializing the changelog for the '%s' repo!" % self.name)
        )
