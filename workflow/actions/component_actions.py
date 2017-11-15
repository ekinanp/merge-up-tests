from file_actions import modify_line
from workflow.utils import sequence
from workflow.constants import VERSION_RE

# This file contains some common component-specific actions that may be useful
# for doing version bumps, updating/adding to CHANGELOGS, releasenotes, etc.

def bump_cpp_project(project_name, version):
    return sequence(
        bump_version("CMakeLists.txt", r'%s VERSION ' % project_name, version),
        bump_version("locales/%s.pot" % project_name, r'Project-Id-Version: %s ' % project_name, version)
    )

def bump_ruby_project(project_name, branch, version, gemspec_branches):
    version_bumps = [bump_version("lib/%s/version.rb" % project_name, "\s+[^\s]*VERSION = ['\"]", version, "['\"]")]
    if branch in gemspec_branches:
        version_bumps.append(bump_version(".gemspec", "\s+version = ['\"]", version, "['\"]"))

    return sequence(*version_bumps)

# prefix is a regex describing the relevant stuff that comes
# before the version, suffix describes the stuff that comes after
# the version
def bump_version(version_file, prefix, version, suffix = ''):
    return modify_line(version_file, r"(%s)%s(%s)" % (prefix, VERSION_RE, suffix), "\g<1>%s\g<2>" % version)
