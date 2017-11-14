import os

from git_repository import GitRepository

class PuppetAgent(GitRepository):
    def __init__(self, github_user, workspace):
        super(PuppetAgent, self).__init__(github_user, 'puppet-agent', workspace, ['1.10.x', '5.3.x', 'master'])

    def component_json(self, component):
        return os.path.join(self.repo_dir, "configs/components/%s.json" % component)
   
    # TODO Modify this code once file_actions.py is implemented
    def bump_component(self, component, branch, new_ref):
        def bump_component_action():
            component_json = self.component_json(component)
            if not os.path.exists(component_json):
                raise Exception("%s is not a component of the puppet-agent in branch %s!" % (component, branch))
