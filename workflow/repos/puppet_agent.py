from workflow.repos.git_repository import (GitRepository, GITHUB_USERNAME)
from workflow.actions.file_actions import update_file
from workflow.utils import commit

# TODO: Might need to include the puppet-agent components as well. The issue is that
# if the puppet-agent happens to reset its branches back to the "clean", "upstream"
# state, the component.jsons will themselves be outdated, which could lead to errors.
class PuppetAgent(GitRepository):
    def __init__(self, github_user = GITHUB_USERNAME, **kwargs):
        kwargs['metadata'] = { 'vanagon_repo' : True }
        repo_name = "puppet-agent-private" if kwargs.get("use_private_fork", False) else "puppet-agent"
        super(PuppetAgent, self).__init__(repo_name, ['1.10.x', '5.3.x', 'master'], github_user, **kwargs)
