import os
import shutil
import subprocess
import tempfile

import unittest

from workflow.utils import in_directory

# This is a base class that stores a temporary workspace to clone/init.
# repos
class RepositoryTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(RepositoryTestCase, self).__init__(*args, **kwargs)
        self.github_fork = os.environ.get('GITHUB_FORK', 'ekinanp')
        self.workspace = tempfile.mkdtemp(prefix='test-pa-workspace')

    def tearDown(self):
        shutil.rmtree(self.workspace)

# cmd should be a list [<arg0>, <arg1>, <arg2> ...]
def in_repo(repo, cmd):
    with in_directory(repo.root):
        stdout = subprocess.check_output(cmd)

    return stdout

