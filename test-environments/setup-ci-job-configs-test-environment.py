import re
import os

from workflow.actions.file_actions import (after_line, new_file, after_lines, modify_lines)
from workflow.repos.git_repository import GitRepository
from workflow.utils import (commit, to_action)

WORKSPACE="/Users/enis.inan/GitHub/puppet-agent-workflow/ci-job-configs-test-environments"
BRANCH_PREFIX = "ci-job-configs-tests" 

def extract_indentation(s):
    return re.match(r"(\s*).*", s).group(1)

def setup_test_environment(repo):
    def add_test_keys(line):
        indent = extract_indentation(line)
        if "nssm" in line: 
            return ""

        return "%s%s\n%s%s" % (indent, "value_stream: 'experimental'", indent, "p_scm_user: 'ekinanp'")  

    def modify_branch_param(param_name):
        return modify_lines("jenkii/jenkins-master-prod-1/projects/puppet-agent.yaml", r"%s: '[Mm]aster'" % param_name, "%s: 'localization-tests-master'" % param_name)

    repo["PA-1175"](
        after_lines("jenkii/jenkins-master-prod-1/projects/puppet-agent.yaml", "p_dn_component_name", add_test_keys),
        modify_branch_param("p_component_branch"),
        modify_branch_param("p_dn_component_branch"),
        modify_branch_param("p_vanagon_branch"),
        commit("Set-up test deployment environment!")
    )

repo = GitRepository("ci-job-configs", ["PA-1175"], workspace = WORKSPACE, stub_prefix = BRANCH_PREFIX)
repo.reset_branch("PA-1175")
setup_test_environment(repo)

repo.in_branch("PA-1175", to_action(os.system)('cjc-manager deploy jenkins-master-prod-1 "*experimental*"'))
