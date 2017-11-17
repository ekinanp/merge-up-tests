from workflow.actions.component_actions import bump_version
from component import Component
from git_repository import (GITHUB_FORK, WORKSPACE)

class MarionetteCollective(Component):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(MarionetteCollective, self).__init__(
            'marionette-collective',
            { "2.10.x": "1.10.x", "2.11.x": "5.3.x", "master": "master"},
            github_user,
            workspace
        )

    # TODO: This should probably be revised to account for changes in
    # website/releasenotes.md, but this can be done later once the CHANGELOG
    # stuff is added
    def _bump(self, branch, version):
        return bump_version("lib/mcollective.rb", 'VERSION="', version, '"')
