from git_repository import (GitRepository, GITHUB_FORK, WORKSPACE)
from workflow.actions.file_actions import update_file
from workflow.utils import commit

# TODO: Might need to include the puppet-agent components as well. The issue is that
# if the puppet-agent happens to reset its branches back to the "clean", "upstream"
# state, the component.jsons will themselves be outdated, which could lead to errors.
class PuppetAgent(GitRepository):
    def __init__(self, github_user = GITHUB_FORK, workspace = WORKSPACE, **kwargs):
        super(PuppetAgent, self).__init__('puppet-agent', ['1.10.x', '5.3.x', 'master'], github_user, workspace, vanagon_repo = True, **kwargs)
