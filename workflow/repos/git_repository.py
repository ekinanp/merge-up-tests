import os
import re
from functools import partial
from tempfile import mkdtemp

from workflow.utils import (in_directory, git, git_action, sequence, validate_input, to_action, push)

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

        self.prompt_push = kwargs.get('prompt_push', False)
        self.remotes = kwargs.get('remotes', { 'upstream' : 'puppetlabs' })
        self.github_user = github_user

        if os.path.exists(self.root):
            self.__prepare_stubs()
            return None

        git('clone %s %s' % (self._git_url(self.github_user, self.name), self.root))
        with in_directory(self.root):
            for (remote_name, remote_user) in self.remotes.items():
                git('remote add %s %s' % (remote_name, self._git_url(remote_user, self.name)))
                git('fetch %s' % remote_name)

            # NOTE: Bit hacky, but it's a way to run some initialization. This should be cleaned
            # up later
            initialize_repo = kwargs.get("initialize_with", None)
            if initialize_repo:
                initialize_repo()

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
          print("\n\nSTARTING CONTEXT ...")
          git('checkout %s' % stub)
          self.__print_context()(self.name, branch)
          return do_action(self.name, branch)

        return self.in_repo(in_repo_action)

    # Each action in "actions" should do something to the repo  It should take the repo name and
    # the branch as parameters (to provide clearer error messages in case something might go wrong).
    #
    # NOTE: Remember that the actual branch being modified is a stub of the passed-in
    # "branch".
    def to_branch(self, branch, *actions, **kwargs):
        prompt_push = self.prompt_push
        if not kwargs.get('prompt_push') is None:
            prompt_push = kwargs.get('prompt_push')

        if kwargs.get('push', False):
            actions = actions + (push('--force', prompt_push), self.__print_context())
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

    def reset_branch(self, branch, **kwargs):
        @to_action
        def print_reset_info():
            print("RESETTING BRANCH %s ..." % branch)

        remote = kwargs.get('remote', 'upstream')
        if remote != "origin" and not remote in self.remotes.keys():
            raise Exception("'%s' is not a part of this repository's remotes!")

        self.in_branch(branch, sequence(
            print_reset_info(),
            git_action('fetch %s' % remote),
            git_action('reset --hard %s/%s' % (remote, branch)),
            git_action('clean -f -d')
        ))

        if kwargs.get('push', False):
            self.in_branch(branch,
                push('--set-upstream origin %s --force' % self.branches[branch], self.prompt_push),
            )

        self.in_branch(branch, self.__print_context())

    def reset_branches(self, **kwargs):
        for branch in self.branches:
            self.reset_branch(branch, **kwargs)

        self.in_repo(lambda : push('--set-upstream origin --tags', self.prompt_push)(self.name, "master"))

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

    def __print_context(self):
        def print_context_action(repo_name, branch):
            print("%s PROJECT-ROOT: %s %s" % ("*" * 4, self.root, "*" * 4))
            print("%s PROJECT-BRANCH: %s %s" % ("*" * 4, branch, "*" * 4))

        return print_context_action
