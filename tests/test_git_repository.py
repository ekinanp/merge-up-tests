import os
import re

from workflow.repository import GitRepository
from workflow.utils import in_directory
from workflow.constants import BRANCH_PREFIX
from utils import (RepositoryTestCase, in_repo)

# TODO: It would be better to mock out all the side-effect stuff (e.g. calls
# to os.path, os.system, etc.) in the future in case this project becomes big enough.
# For now, these tests are good enough. <-- Actually, should mock some stuff out.
# Come back to testing once this is figured out.
#
# TODO: Refactor so that the test_repo is created only once.
#
# TODO: Add tests for in_branch (exception thrown) and reset_repo
class GitRepositoryTestCase(RepositoryTestCase):
    def setUp(self):
        self.test_branches = ['1.10.x', '5.3.x', 'master']
        self.test_repo = GitRepository(self.github_fork, 'puppet-agent', self.self.test_branches)

    # TODO: Add test to ensure that repo is not re-created if self.root already
    # exists!
    def test_init(self):
        assert os.path.exists(self.test_repo.root), 'puppet-agent directory was not properly created!'

        created_branches = in_repo(self.test_repo, ['git', 'branch']).split("\n")
        created_branches = [re.sub('[ *]', '', branch) for branch in created_branches] 
        for branch in self.test_branches:
            assert (("%s-%s" % (BRANCH_PREFIX, branch)) in created_branches), 'The stub for branch %s was not properly created!' % branch

    def test_in_branch(self):
        test_files = [("pa-workflow-test-git-repository-%s" % test_file) for test_file in ["test-one", "test-two"]]
        commit_msg = "Testing out a simulated workflow!"
        def create_test_files():
            for test_file in test_files:
                open(test_file, 'a').close()

            return (test_files, commit_msg)

        self.test_repo.in_branch('1.10.x', create_test_files)

        git_log_results = in_repo(self.test_repo, ['git', 'log', '-1', '--stat'])

        assert (commit_msg in git_log_results), 'The desired commit does not exist!'
        for test_file in test_files:
            assert(test_file in git_log_results), 'The %s file was not successfully created!' % test_file
        # TODO: Check that the files were also pushed up (in the future)


# TODO: Find a better way to get stuff to run so that this boilerplate
# can be removed.
if __name__ == '__main__':
    unittest.main()
