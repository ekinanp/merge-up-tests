from workflow.actions.component_actions import bump_version_file
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)

class MarionetteCollective(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(MarionetteCollective, self).__init__(
            'marionette-collective',
            { "2.10.x": "1.10.x", "2.11.x": "5.3.x", "master": "master"},
            github_user,
            workspace,
            version_bumper = bump_version_file("lib/mcollective.rb", 'VERSION="', '"')
        )
