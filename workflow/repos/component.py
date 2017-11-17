import re

from git_repository import (GitRepository, GITHUB_FORK, WORKSPACE)
from puppet_agent import PuppetAgent
from workflow.actions.file_actions import update_file
from workflow.utils import (in_directory, to_action, commit, flatten, exec_stdout, validate_version)
from workflow.constants import VERSION_RE

class Component(GitRepository):
    # Here, the "pa_branches" parameter is a map of <component_branch> -> [<puppet_agent_branch>].,
    #
    # NOTE: Might not be a bad idea to pass in the puppet_agent repo as a parameter to the
    # constructor.
    def __init__(self, component_name, pa_branches, github_user, workspace, **kwargs):
        super(Component, self).__init__(component_name, pa_branches.keys(), github_user, workspace, **kwargs)
        self.pa_branches = {branch: flatten(pa_branches[branch]) for branch in pa_branches}
        self.puppet_agent = PuppetAgent(github_user, workspace)

        # Now update the component URLs (if they have not already been updated) in the puppet-agent
        # repo
        component_url = super(Component, self.__class__)._git_url(github_user, self.name)
        for pa_branch in set(flatten(self.pa_branches.values())):
            self.puppet_agent.update_component_json(
                self.name,
                pa_branch,
                'url',
                component_url,
                "Initialized the '%s' component's url!" % self.name
            )

    def to_branch(self, branch, *actions):
        super(Component, self).to_branch(branch, *actions)
        self.__update_ref(branch)

    def reset_branch(self, branch):
        super(Component, self).reset_branch(branch)
        self.__update_ref(branch)

    @validate_version(2)
    def bump(self, branch, version):
        self.to_branch(
            branch,
            self._bump(branch, version),
            commit("Bumped %s to %s!" % (self.name, version))
        )

    # This method should return an action which contains all the necessary code to version-bump
    # the component
    def _bump(self, branch, version):
        raise NotImplementedError()

    def __update_ref(self, branch):
        sha = self.in_branch(branch, exec_stdout('git', 'rev-parse', 'HEAD'))
        for pa_branch in self.pa_branches[branch]:
            self.puppet_agent.bump_component(self.name, pa_branch, sha)
