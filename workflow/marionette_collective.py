from component_actions import bump_version
from component import Component

class MarionetteCollective(Component):
    def __init__(self, github_user, workspace):
        super(MarionetteCollective, self).__init__(
            github_user,
            'marionette-collective',
            workspace,
            { "2.10.x": "1.10.x", "2.11.x": "5.3.x", "master": "master"}
        )

    # TODO: This should probably be revised to account for changes in
    # website/releasenotes.md, but this can be done later once the CHANGELOG
    # stuff is added
    def _bump(self, branch, version):
        return bump_version("lib/mcollective.rb", 'VERSION="', version, '"')
