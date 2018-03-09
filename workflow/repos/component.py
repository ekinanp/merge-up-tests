import re

from workflow.repos.git_repository import (GitRepository, GITHUB_USERNAME)
from workflow.repos.puppet_agent import PuppetAgent
from workflow.utils import (in_directory, commit, flatten, git_head)
from workflow.constants import VERSION_RE
from workflow.actions.repo_actions import (bump_component, update_component_json)

class Component(GitRepository):
    # Here, the "pa_branches" parameter is a map of <component_branch> -> [<puppet_agent_branch>].,
    #
    # NOTE: Might not be a bad idea to pass in the puppet_agent repo as a parameter to the
    # constructor.
    def __init__(self, component_name, pa_branches, github_user, **kwargs):
        self.pa_branches = {branch: flatten(pa_branches[branch]) for branch in pa_branches}
        self.puppet_agent = kwargs['puppet_agent']
        self.update_ref = kwargs.get('update_ref', False)
        self.is_private_fork = kwargs.get("use_private_fork", False)
        self.component_name = component_name
        repo_name = self.component_name
        if self.is_private_fork:
            repo_name += "-private"
        super(Component, self).__init__(repo_name, pa_branches.keys(), github_user, **kwargs)

    def to_branch(self, branch, *actions, **kwargs):
        super(Component, self).to_branch(branch, *actions, **kwargs)
        if self.update_ref or kwargs.get('update_ref', None):
            self.__update_ref(branch, **kwargs)

    def reset_branch(self, branch, **kwargs):
        super(Component, self).reset_branch(branch)
        if self.update_ref or kwargs.get('update_ref', None):
            self.__update_ref(branch, **kwargs)

    def update_url(self, branch, **kwargs):
        print("\n\nABOUT TO UPDATE COMPONENT %s's URL IN ITS COMPONENT.JSON FILE ..." % self.component_name)
        print("THIS WILL HAPPEN IN THE %s BRANCHES OF THE PUPPET AGENT" % ', '.join(self.pa_branches[branch]))

        component_url = super(Component, self.__class__)._git_url(self.github_user, self.name)
        for pa_branch in self.pa_branches[branch]:
            self.puppet_agent[pa_branch](
                update_component_json(self.component_name, 'url', component_url),
                commit("Updated the '%s' component's url!" % self.component_name),
                **kwargs
            )

    def update_urls(self, **kwargs):
        for branch in self.branches:
            self.update_url(branch, **kwargs)

    def __update_ref(self, branch, **kwargs):
        print("\n\nABOUT TO BUMP COMPONENT %s's REF IN ITS COMPONENT.JSON FILE ..." % self.component_name)
        print("THIS WILL HAPPEN IN THE %s BRANCHES OF THE PUPPET AGENT" % ', '.join(self.pa_branches[branch]))

        print("GETTING THE HEAD SHA FIRST ...")
        sha = self.in_branch(branch, git_head).decode("utf-8")
        print("\nNOW DOING THE BUMPS ...")
        for pa_branch in self.pa_branches[branch]:
            self.puppet_agent[pa_branch](
                bump_component(self.component_name, sha),
                commit("Bumping '%s' to '%s'!" % (self.component_name, sha)),
                **kwargs
            )
