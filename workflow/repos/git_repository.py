import os
from functools import partial

from workflow.utils import (in_directory, git, git_action, sequence, validate_input)

def _default_workspace():
    path = os.path
    project_root = path.dirname(path.dirname(path.realpath(__file__)))
    return path.join(project_root, 'workspace')

GITHUB_FORK = os.environ.get('GITHUB_FORK', 'ekinanp')
WORKSPACE = os.environ.get('PA_WORKSPACE', _default_workspace()) 
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

    @staticmethod
    def __stub_branch(branch):
        return BRANCH_PREFIX + "-" + branch

    @classmethod
    def _add_repo_metadata(cls, repo_name, key, metadata):
        cur_metadata = cls.repo_metadata.get(repo_name)
        if not cur_metadata:
            cls.repo_metadata[repo_name] = {}

        cls.repo_metadata[repo_name][key] = metadata

    def __init__(self, repo_name, branches, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        self.name = repo_name
        self.root = os.path.join(workspace, repo_name)
        # Map of <base-branch> -> <stubbed-branch>. This is to avoid messing with special
        # stuff that people might have on their forks when simulating the workflow.
        self.branches = dict([[branch, BRANCH_PREFIX + "-" + branch] for branch in branches])

        for key in kwargs:
            self.__class__._add_repo_metadata(self.name, key, kwargs[key])

        if os.path.exists(self.root):
            return None

        git('clone %s %s' % (self._git_url(github_user, self.name), self.root))
        with in_directory(self.root):
            git('remote add upstream %s' % self._git_url('puppetlabs', self.name))
            git('fetch upstream')

        self.reset_branches()

    def in_branch(self, branch, do_action):
        stub = self.branches.get(branch)
        if stub is None:
            raise Exception("Only the [%s] branches of the '%s' repo are write-permissible!" % (', '.join(self.branches.keys()), self.name)) 

        with in_directory(self.root):
          git('checkout %s' % stub)
          return do_action(self.name, branch)

    # Each action in "actions" should do something to the repo  It should take the repo name and
    # the branch as parameters (to provide clearer error messages in case something might go wrong).
    #
    # NOTE: Remember that the actual branch being modified is a stub of the passed-in
    # "branch".
    def to_branch(self, branch, *actions):
        actions = actions + (git_action('push'),)
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
            git_action('push --set-upstream origin --force')
        ))

    def reset_branches(self):
        for branch in self.branches:
            self.reset_branch(branch)
