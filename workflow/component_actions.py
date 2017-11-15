from file_actions import replace_line
from utils import sequence
from constants import VERSION_RE

# This file contains some common component-specific actions that may be useful
# for doing version bumps, updating/adding to CHANGELOGS, releasenotes, etc.

def bump_cpp_project(project_name, version):
    cmake_str = version_str(r'%s VERSION {vn}' % project_name)
    pot_str = version_str(r'Project-Id-Version: %s {vn}' % project_name)

    return sequence(
        replace_line("CMakeLists.txt", cmake_str(VERSION_RE), cmake_str(version)),
        replace_line("locales/%s.pot" % project_name, pot_str(VERSION_RE), pot_str(version))
    )

def version_str(template):
    return lambda version: template.format(vn = version)
