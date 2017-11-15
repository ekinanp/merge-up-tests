from contextlib import contextmanager
import os

from constants import BRANCH_PREFIX
from utils import (in_directory, git, sequence)

_path = os.path

# NOTE: http://gitpython.readthedocs.io/en/stable/ is a convenient package
# that might help here. This initial iteration is to prevent people from having
# to setup pip, which can get complicated.
#
# TODO: Might be worthwhile to revise the in_branch method to just take a generic action
# that resides inside the branch -- it returns whatever the action returns. Actions that
# don't do anything can return "None" (e.g. like the existing code which just pushes stuff
# up to the repo). That way, we can do things like 'git rev-parse HEAD', push stuff up, etc.
# This might require a refactor elsewhere in the codebase, but it will probably be worth it.
# This should be a design consideration once other stuff (e.g. version bumps, CHANGELOG updates)
# have been implemented
class GitRepository(object):
    'Base class for a generic git repository'

    @staticmethod
    def _git_url(github_user, repo_name):
        return "git@github.com:%s/%s.git" % (github_user, repo_name)

    @staticmethod
    def __stub_branch(branch):
        return BRANCH_PREFIX + "-" + branch

    def __init__(self, github_user, repo_name, workspace, branches):
        self.name = repo_name
        self.root = _path.join(workspace, repo_name)
        # Map of <base-branch> -> <stubbed-branch>. This is to avoid messing with special
        # stuff that people might have on their forks when simulating the workflow.
        self.branches = dict([[branch, BRANCH_PREFIX + "-" + branch] for branch in branches])

        if _path.exists(self.root):
            return None

        git('clone %s %s' % (self._git_url(github_user, self.name), self.root))
        with in_directory(self.root):
            git('remote add upstream %s' % self._git_url('puppetlabs', self.name))
            git('fetch upstream')

        self.reset_branches()

    # Each action in "actions" should do something to the repo  It should take the repo name and
    # the branch as parameters (to provide clearer error messages in case something might go wrong).
    #
    # NOTE: Remember that the actual branch being modified is a stub of the passed-in
    # "branch".
    def in_branch(self, branch, *actions):
        stub = self.branches.get(branch)
        if stub is None:
            raise Exception("Only the [%s] branches of the '%s' repo are write-permissible!" % (', '.join(self.branches.keys()), self.name)) 

        with in_directory(self.root):
          git('checkout %s' % stub)
          sequence(*actions)(self.name, branch)
          git('push')

    def reset_branches(self):
        dummy_branch = 'fewafweafafea'
        with in_directory(self.root):
            git('stash')
            git('checkout -b %s' % dummy_branch)
            for base in self.branches:
                stub = self.branches[base]
                git('branch -D %s' % stub)
                git('checkout -b %s upstream/%s' % (stub, base))
                git('push --set-upstream origin %s --force' % stub)
            git('branch -D %s' % dummy_branch)
