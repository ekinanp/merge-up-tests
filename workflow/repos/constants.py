from workflow.actions.repo_actions import (bump_cpp_project, bump_ruby_project, bump_version_file, sequence)
from workflow.repos.git_repository import (GitRepository, GITHUB_USERNAME)
from workflow.repos.component import (Component)

import os

def workspace(ticket):
    return "%s/%s/%s" % (os.environ['HOME'], "GitHub/puppet-agent-workflow/workspaces", ticket)

# TODO: Add a version bumper to puppet-agent!
def __puppet_agent(github_user = GITHUB_USERNAME, **kwargs):
    kwargs['metadata'] = {
        'vanagon_repo' : True,
        'version_bumper' : bump_version_file("VERSION", '', '')
    }
    repo_name = "puppet-agent-private" if kwargs.get("use_private_fork", False) else "puppet-agent"
    branches = [
        '1.10.x',
        '5.3.x',
        '5.5.x',
        'master'
    ]
    return GitRepository(repo_name, branches, github_user, **kwargs)

def __leatherman(github_user = GITHUB_USERNAME, **kwargs):
    kwargs['metadata'] = {
        'version_bumper' : bump_cpp_project('leatherman')
    }
    pa_branches = {
        "0.12.x": "1.10.x",
        "1.2.x": "5.3.x",
        "1.4.x": "5.5.x",
        "master": "master",
    }

    return Component('leatherman', pa_branches, github_user, **kwargs) 

def __pxp_agent(github_user = GITHUB_USERNAME, **kwargs):
    kwargs['metadata'] = {
        'version_bumper' : bump_cpp_project('pxp-agent')
    }
    pa_branches = {
        "1.5.x": "1.10.x",
        "1.8.x": "5.3.x",
        "1.9.x": "5.5.x",
        "master": "master",
    }

    return Component('pxp-agent', pa_branches, github_user, **kwargs) 

def __cpp_pcp_client(github_user = GITHUB_USERNAME, **kwargs):
    kwargs['metadata'] = {
        'version_bumper' : bump_cpp_project('cpp-pcp-client')
    }
    pa_branches = {
        "1.5.x": [ "1.10.x", "5.3.x", "5.5.x" ],
        "master": "master",
    }

    return Component('cpp-pcp-client', pa_branches, github_user, **kwargs)

def __libwhereami(github_user = GITHUB_USERNAME, **kwargs):
    kwargs['metadata'] = {
        'version_bumper' : bump_cpp_project('whereami')
    }
    pa_branches = {
        "0.1.x": "5.3.x",
        "0.2.x": "5.5.x",
        "master": "master",
    }

    return Component('libwhereami', pa_branches, github_user, **kwargs)


def __facter(github_user = GITHUB_USERNAME, **kwargs):
    kwargs['metadata'] = {
        'version_bumper' : sequence(
            bump_cpp_project('FACTER'),
            bump_version_file("lib/Doxyfile", r'PROJECT_NUMBER\s+=\s+')
        )
    }
    pa_branches = {
        "3.6.x": "1.10.x",
        "3.9.x": "5.3.x",
        "3.11.x": "5.5.x",
        "master": "master",
    }

    return Component('facter', pa_branches, github_user, **kwargs) 

def __hiera(github_user = GITHUB_USERNAME, **kwargs):
    kwargs['metadata'] = {
        'version_bumper' : bump_ruby_project('hiera', ["3.4.x", "master"])
    }
    pa_branches = {
        "3.3.x": "1.10.x",
        "3.4.x": [ "5.3.x", "5.5.x" ],
        "master": "master",
    }

    return Component('hiera', pa_branches, github_user, **kwargs) 

def __puppet(github_user = GITHUB_USERNAME, **kwargs):
    kwargs['metadata'] = {
        'version_bumper' : bump_ruby_project('puppet', ["5.3.x", "5.5.x", "master"])
    }
    pa_branches = {
        "4.10.x": "1.10.x",
        "5.3.x": "5.3.x",
        "5.5.x": "5.5.x",
        "master": "master",
    }

    return Component('puppet', pa_branches, github_user, **kwargs) 

def __marionette_collective(github_user = GITHUB_USERNAME, **kwargs):
    kwargs['metadata'] = {
        'version_bumper' : bump_version_file("lib/mcollective.rb", 'VERSION="', '"')
    }
    pa_branches = {
        "2.10.x": "1.10.x",
        "2.11.x": "5.3.x",
        "2.12.x": "5.5.x",
        "master": "master",
    }

    return Component('marionette-collective', pa_branches, github_user, **kwargs) 

REPOS = {
    'puppet-agent' : __puppet_agent,
    'leatherman' : __leatherman,
    'pxp-agent' : __pxp_agent,
    'cpp-pcp-client' : __cpp_pcp_client,
    'libwhereami' : __libwhereami,
    'facter' : __facter,
    'hiera' : __hiera,
    'puppet' : __puppet,
    'marionette_collective' : __marionette_collective,
}
