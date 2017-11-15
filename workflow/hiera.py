from component_actions import bump_ruby_project
from component import Component

class Hiera(Component):
    def __init__(self, github_user, workspace):
        super(Hiera, self).__init__(
            github_user,
            'hiera',
            workspace,
            { "3.3.x": "1.10.x", "3.4.x": "5.3.x", "master": "master"}
        )

    def _bump(self, branch, version):
        return bump_ruby_project(self.name, branch, version, ["3.4.x", "master"])
