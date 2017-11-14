import os

def _default_workspace():
    path = os.path
    project_root = path.dirname(path.dirname(path.realpath(__file__)))
    return path.join(project_root, 'workspace')

GITHUB_FORK = os.environ.get('GITHUB_FORK', 'ekinanp')
WORKSPACE = os.environ.get('PA_WORKSPACE', _default_workspace()) 
BRANCH_PREFIX = os.environ.get('BRANCH_PREFIX', 'PA-1706')
