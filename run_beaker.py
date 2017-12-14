from workflow.repos.git_repository import GitRepository
from workflow.utils import (in_directory, identity)
from workflow.beaker_timing.beaker_runner import BeakerRunner

import os
import sys

WORKSPACE = os.environ("WORKSPACE")

REPO_INFO = {
    "puppet-agent" : False,
    "pxp-agent" : True,
    "puppet" : True
}

USAGE = "USAGE: python run_beaker.py <repo-name>"

if len(sys.argv) < 2:
    print(USAGE)
    sys.exit(1)

repo_name = sys.argv[1]
needs_master = REPO_INFO[repo_name]
rake_task = "acceptance:development" if repo_name == "puppet-agent" else "ci:test:aio"

repo = GitRepository(repo_name, ["pa-timing"], workspace = WORKSPACE, stub_branch = identity)
runner = BeakerRunner(rake_task, needs_master)

repo.in_branch(
    "pa-timing",
    runner.action(os.environ("TEST_TARGET"))
)
