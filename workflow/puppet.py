from component_actions import bump_ruby_project
from component import Component

class Puppet(Component):
    def __init__(self, github_user, workspace):
        super(Puppet, self).__init__(
            github_user,
            'puppet',
            workspace,
            { "4.10.x": "1.10.x", "5.3.x": "5.3.x", "master": "master"}
        )

    def _bump(self, branch, version):
        return bump_ruby_project(self.name, branch, version, ["5.3.x", "master"])
