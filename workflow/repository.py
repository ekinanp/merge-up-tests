from contextlib import contextmanager
import os

from constants import BRANCH_PREFIX
from utils import (in_directory, git)

_path = os.path

# NOTE: http://gitpython.readthedocs.io/en/stable/ is a convenient package
# that might help here. This initial iteration is to prevent people from having
# to setup pip, which can get complicated.
class GitRepository:
    'Base class for a generic git repository'

    @staticmethod
    def __git_url(github_user, repo_name):
        return "git@github.com:%s/%s.git" % (github_user, repo_name)

    @staticmethod
    def __stub_branch(branch):
        return BRANCH_PREFIX + "-" + branch

    def __init__(self, github_user, repo_name, workspace, branches):
        self.name = repo_name
        self.root = _path.join(workspace, self.name)
        # Map of <base-branch> -> <stubbed-branch>. This is to avoid messing with special
        # stuff that people might have on their forks when simulating the workflow.
        self.branches = dict([[branch, BRANCH_PREFIX + "-" + branch] for branch in branches])

        if _path.exists(self.root):
            return None

        git('clone %s %s' % (self.__git_url(github_user, self.name), self.root))
        with in_directory(self.root):
            git('remote add upstream %s' % self.__git_url('puppetlabs', self.name))
            git('fetch upstream')

        self.reset_repo()

    # do_action should return a tuple (affected_files, commit_msg)
    def in_branch(self, branch, do_action):
        stub = self.branches.get(branch)
        if stub is None:
            raise Exception("Only the [%s] branches of the '%s' repo are write-permissible!" % (', '.join(self.branches.keys), self.name)) 

        with in_directory(self.root):
          git('checkout %s' % stub)
          (affected_files, commit_msg) = do_action()
          for affected_file in affected_files:
              git('add %s' % affected_file)
          git('commit -m "%s"' % commit_msg)
          git('push')

    def reset_repo(self):
        with in_directory(self.root):
            for base in self.branches:
                stub = self.branches[base]
                git('branch -D %s' % stub)
                git('checkout -b %s upstream/%s' % (stub, base))
                git('push --set-upstream origin %s --force' % stub)
