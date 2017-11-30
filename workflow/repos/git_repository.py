import os
import re
from functools import partial
from tempfile import mkdtemp

from workflow.utils import (in_directory, git, git_action, sequence, validate_input)

GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', '')
BRANCH_PREFIX = os.environ.get('BRANCH_PREFIX', 'PA-1706')

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

    # Stores metadata about the repo, such as its Changelog information, version bumper,
    # etc.
    #
    # TODO: Probably a better way to do this stuff. Refactor so that we don't have to store
    # this info. as class variables
    repo_metadata = {}

    # Checks if the desired metadata exists for the given repo. This is so actions can query
    # the repo_metadata.
    @staticmethod
    def metadata_exists(entry):
        def metadata_validator(repo_name):
            try:
                return GitRepository.repo_metadata[repo_name][entry]
            except:
                return False

        return validate_input(metadata_validator, 0, "Repo '%s' does not have an entry for '{_entry}'!".format(_entry = entry))

    @staticmethod
    def _git_url(github_user, repo_name):
        return "git@github.com:%s/%s.git" % (github_user, repo_name)

    @classmethod
    def _add_repo_metadata(cls, repo_name, key, metadata):
        cur_metadata = cls.repo_metadata.get(repo_name)
        if not cur_metadata:
            cls.repo_metadata[repo_name] = {}

        cls.repo_metadata[repo_name][key] = metadata

    def __init__(self, repo_name, branches, github_user = GITHUB_USERNAME, **kwargs):
        if not github_user:
            raise Exception("github_user cannot be empty! Use the environment variable GITHUB_USERNAME instead!")

        self.name = repo_name
        self.workspace = kwargs.get('workspace')
        if not self.workspace:
            self.workspace = mkdtemp(prefix = 'tmp-workspace')
        self.root = os.path.join(self.workspace, self.name)

        # Map of <base-branch> -> <stubbed-branch>. This is to avoid messing with special
        # stuff that people might have on their forks when simulating the workflow.
        self.stub_branch = kwargs.get('stub_branch', lambda branch: kwargs.get('stub_prefix', BRANCH_PREFIX) + "-" + branch)
        self.branches = dict([[branch, self.stub_branch(branch)] for branch in branches])

        metadata = kwargs.get('metadata', {})
        for key in metadata:
            self.__class__._add_repo_metadata(self.name, key, metadata[key])

        if os.path.exists(self.root):
            self.__prepare_stubs()
            return None

        git('clone %s %s' % (self._git_url(github_user, self.name), self.root))
        with in_directory(self.root):
            git('remote add upstream %s' % self._git_url('puppetlabs', self.name))
            git('fetch upstream')

        self.__prepare_stubs()

    # TODO: Refactor in_repo, in_branch and to_branch to make their uniformity
    # clearer. This workaround is just to make it easier to test stuff.
    def in_repo(self, do_action):
        with in_directory(self.root):
            return do_action()

    def in_branch(self, branch, do_action):
        stub = self.branches.get(branch)
        if stub is None:
            raise Exception("Only the [%s] branches of the '%s' repo are write-permissible!" % (', '.join(self.branches.keys()), self.name))

        def in_repo_action():
          git('checkout %s' % stub)
          return do_action(self.name, branch)

        return self.in_repo(in_repo_action)

    # Each action in "actions" should do something to the repo  It should take the repo name and
    # the branch as parameters (to provide clearer error messages in case something might go wrong).
    #
    # NOTE: Remember that the actual branch being modified is a stub of the passed-in
    # "branch".
    def to_branch(self, branch, *actions, **kwargs):
        def push_action(repo, branch):
            if not kwargs.get('prompt_push'):
                git('push')
                return

            user_response = raw_input("\n\nWould you like to push your changes to 'origin'? ")
            if re.match(r'^(?:y|Y|%s)$' % '|'.join(["%s%s%s" % (l1, l2, l3) for l1 in ['y', 'Y'] for l2 in ['e', 'E'] for l3 in ['s', 'S']]), user_response):
                print("You answered 'Yes'! Pushing your changes to 'origin' ...")
                git('push')
            else:
                print("You answered 'No'! Your changes will not be pushed.")

            print("%s WORKSPACE: %s %s" % ("*" * 4, self.workspace, "*" * 4))

        actions = actions + (push_action,)
        self.in_branch(branch, sequence(*actions))

    # This allows for more intuitive syntax like (using "facter" as an example):
    #   facter['3.6.x'](
    #     <first action>,
    #     <second action>,
    #     ...
    #   )
    #
    # TODO: Extend this so it can handle something like:
    #   facter['3.6.x', '5.3.x', ...](
    #   )
    # which means "In branches 3.6.x and 5.3.x of facter do ..."
    def __getitem__(self, branch):
        return partial(self.to_branch, branch)

    def reset_branch(self, branch):
        self.in_branch(branch, sequence(
            git_action('fetch upstream'),
            git_action('reset --hard upstream/%s' % branch),
            git_action('clean -f -d'),
            git_action('push --set-upstream origin %s --force' % self.branches[branch])
        ))

    def reset_branches(self):
        for branch in self.branches:
            self.reset_branch(branch)

    def __prepare_stubs(self):
        # Ensure the branches are checked out
        branch_exists = lambda git_branch : self.in_repo(lambda : git('show-branch %s' % git_branch)) == 0
        for branch in self.branches:
            stub = self.branches[branch]
            if branch_exists(stub):
                continue

            if branch_exists("remotes/origin/%s" % stub):
                self.in_repo(lambda : git("checkout -b %s origin/%s" % (stub, stub)))
                continue

            self.in_repo(lambda : git("checkout -b %s" % stub))
            self.reset_branch(branch)
