import json

from git_repository import GitRepository
from file_actions import update_file
from utils import commit

# TODO: Might need to include the puppet-agent components as well. The issue is that
# if the puppet-agent happens to reset its branches back to the "clean", "upstream"
# state, the component.jsons will themselves be outdated, which could lead to errors.
class PuppetAgent(GitRepository):
    def __init__(self, github_user, workspace):
        super(PuppetAgent, self).__init__(github_user, 'puppet-agent', workspace, ['1.10.x', '5.3.x', 'master'])

    def component_json(self, component):
        return "configs/components/%s.json" % component
   
    def bump_component(self, component, branch, new_ref):
        self.update_component_json(component, branch, 'ref', new_ref, 'Bumping %s to %s!' % (component, new_ref))

    def update_component_json(self, component, branch, key, new_value, commit_msg):
        def update_component_json_action(f, ftemp):
            component_info = json.loads(f.read())
            component_info[key] = new_value
            ftemp.write(json.dumps(component_info))

        super(PuppetAgent, self).in_branch(
                branch,
                update_file(self.component_json(component), update_component_json_action),
                commit(commit_msg)
        )
