from workflow.actions.repo_actions import bump_ruby_project
from workflow.repos.component import Component
from workflow.repos.git_repository import GITHUB_USERNAME

class Puppet(Component):
    def __init__(self, github_user = GITHUB_USERNAME, **kwargs):
        kwargs['metadata'] = {
            'version_bumper' : bump_ruby_project('puppet', ["5.3.x", "master"])
        }

        super(Puppet, self).__init__(
            'puppet',
            { "4.10.x": "1.10.x", "5.3.x": "5.3.x", "master": "master"},
            github_user,
            **kwargs
        )
