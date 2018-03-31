from functools import partial
import json
import re

from workflow.actions.file_actions import (modify_line, read_file, rewrite_file, update_file)
from workflow.repos.git_repository import GitRepository
from workflow.utils import (commit, const, validate_version, git)
from workflow.constants import VERSION_RE
import workflow.utils as utils

metadata_exists = GitRepository.metadata_exists

# This file contains some common component-specific actions that may be useful
# for doing version bumps, updating/adding to CHANGELOGS, releasenotes, etc.

# In English, this is saying:
#   "Take all of the version bumper actions, create them, and then execute them in order"
def sequence(*version_bumpers):
    return lambda version: utils.sequence(*[version_bumper(version) for version_bumper in version_bumpers])

def bump_cpp_project(project_name):
    return sequence(
        bump_version_file("CMakeLists.txt", r'%s VERSION ' % project_name),
        bump_version_file("locales/%s.pot" % project_name, r'Project-Id-Version: %s ' % project_name)
    )

def bump_ruby_project(project_name, gemspec_branches):
    def bump_ruby_project_action(version, repo_name, branch):
        version_bumps = [bump_version_file("lib/%s/version.rb" % project_name, "\s+[^\s]*VERSION = ['\"]", "['\"]")]
        if branch in gemspec_branches:
            version_bumps.append(bump_version_file(".gemspec", "\s+version = ['\"]", "['\"]"))

        sequence(*version_bumps)(version)(repo_name, branch)

    return lambda version: partial(bump_ruby_project_action, version)

# prefix is a regex describing the relevant stuff that comes
# before the version, suffix describes the stuff that comes after
# the version
def bump_version_file(version_file, prefix, suffix = ''):
    return lambda version: modify_line(version_file, r"(%s)%s(%s)" % (prefix, VERSION_RE, suffix), "\g<1>%s\g<2>" % version)

def read_version(repo_name, branch):
    def read_version_file(path, prefix_regex, suffix_regex):
        matching_regex = re.compile("%s%s%s" % (prefix_regex, "([0-9]+\.[0-9]+\.[0-9]+)", suffix_regex))
        file_contents = read_file(path)(repo_name, branch)
        match_obj = re.search(matching_regex, read_file(path)(repo_name, branch))

        return (match_obj.group(1) or None)

    hash_map = {
         "VERSION"                       : ['', ''],
         "CMakeLists.txt"                : ["project\([\w-]+ VERSION ", "\)"],
         "lib/%s/version.rb" % repo_name : ["[^\s]*VERSION = [\'\"]", "[\'\"]"],
         "lib/mcollective.rb"            : ["\s*VERSION=[\'\"]", "[\'\"]"],
    }
    for path, (prefix, suffix) in hash_map.items():
        try:
            return read_version_file(path, prefix, suffix)
        except:
            pass
 
    raise Exception("Not a versioned repo!")

    return read_version_action

@validate_version(0)
def bump_version(version):
    @metadata_exists('version_bumper')
    def bump_version_action(repo_name, branch):
        version_bumper = GitRepository.repo_metadata[repo_name]['version_bumper']
        version_bumper(version)(repo_name, branch)
        commit("Bumping %s to %s!" % (repo_name, version))(repo_name, branch)

    return bump_version_action

def update_component_json(component, key, new_value):
    @metadata_exists('vanagon_repo')
    def update_component_json_action(repo_name, branch):
        def modify_component_json_file(f, ftemp):
            component_info = json.loads(f.read())
            component_info[key] = new_value

            ftemp.write(json.dumps(component_info))

        return update_file("configs/components/%s.json" % component, modify_component_json_file)(repo_name, branch)

    return update_component_json_action

def bump_component(component, new_ref):
    return update_component_json(component, "ref", new_ref)

# action should take the changelog as its argument
def to_changelog_action(action):
    @metadata_exists('changelog')
    def changelog_action(repo_name, branch):
        (changelog_type, changelog_path) = GitRepository.repo_metadata[repo_name]['changelog']
        changelog_contents =  read_file(changelog_path)(repo_name, branch)
        changelog = changelog_type(changelog_contents)
        action(changelog)
        rewrite_file(changelog_path, changelog.render())(repo_name, branch)

    return changelog_action

# returns an action that updates a component's change log.
def update_changelog(*args, **kwargs):
    return to_changelog_action(lambda changelog : changelog.update(*args, **kwargs))
