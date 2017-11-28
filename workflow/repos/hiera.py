from workflow.actions.repo_actions import bump_ruby_project
from component import Component
from git_repository import GITHUB_FORK

class Hiera(Component):
    def __init__(self, github_user = GITHUB_FORK, **kwargs):
        kwargs['metadata'] = {
            'version_bumper' : bump_ruby_project('hiera', ["3.4.x", "master"])
        }

        super(Hiera, self).__init__(
            'hiera',
            { "3.3.x": "1.10.x", "3.4.x": "5.3.x", "master": "master"},
            github_user,
            **kwargs
        )
