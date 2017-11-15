import subprocess
import re

from git_repository import (GitRepository, GITHUB_FORK, WORKSPACE)
from puppet_agent import PuppetAgent
from workflow.actions.file_actions import update_file
from workflow.utils import (in_directory, commit, flatten)
from workflow.constants import VERSION_RE

# TODO: Need to consider the case when the component resets itself -- should update the
# corresponding component ref in the puppet-agent. This should be done once in_branch
# is updated, to make the code changes easier.
class Component(GitRepository):
    # Here, the "pa_branches" parameter is a map of <component_branch> -> [<puppet_agent_branch>].,
    #
    # NOTE: Might not be a bad idea to pass in the puppet_agent repo as a parameter to the
    # constructor.
    def __init__(self, component_name, pa_branches, github_user, workspace):
        super(Component, self).__init__(component_name, pa_branches.keys(), github_user, workspace)
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

    def in_branch(self, branch, *actions):
        super(Component, self).in_branch(branch, *actions)
        with in_directory(self.root):
            sha = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()

        for pa_branch in self.pa_branches[branch]:
            self.puppet_agent.bump_component(self.name, pa_branch, sha)

    def bump(self, branch, version):
        if re.match(VERSION_RE, version) is None: 
            raise Exception("Version %s is not of the form x.y.z!" % version)

        self.in_branch(
            branch,
            self._bump(branch, version),
            commit("Bumped %s to %s!" % (self.name, version))
        )

    # This method should return an action which contains all the necessary code to version-bump
    # the component
    def _bump(self, branch, version):
        raise NotImplementedError()
