import os
import re

from workflow.utils import (git, find_some, validate_input)
from functools import partial

# This module contains some useful functions that are used to create actions capturing
# CRUD operations on files (save for the "R" part). These actions only make sense on a
# GitRepository object
#
# Using the functions here, we can write things like
#   facter['3.6.x'](
#     update_file('Makefile', <code here>),
#     create_file('some feature', <code here>),
#     commit("Doing stuff!")
#   ) 
#
# Each "action" should take the repo name and the branch as parameters (to provide
# clearer error messages on what might go wrong). 
#
# TODO: Add "after_line", "before_line", "modify_lines" when time permits.
#
# TODO: For some stupid reason, Python inserts an extra EOF character at the end
# of a text file after writing it. This shows up as a red circle in the Git diff.
# when doing a PR in GitHub. See if there's a way to remove this, although that
# isn't really top priority

def modify_line(file_path, line_re, substitution):
    return modify_lines(file_path, line_re, substitution, 1)

def modify_lines(file_path, line_re, substitution, n = -1):
    return map_lines(file_path, line_re, lambda line: re.sub(line_re, substitution, line), n)

def after_line(file_path, line_re, generate_contents):
    return after_lines(file_path, line_re, generate_contents, 1)

def after_lines(file_path, line_re, generate_contents, n = -1):
    return map_lines(file_path, line_re, lambda line: "%s\n%s\n" % (line[:-1], generate_contents(line)), n)

def before_line(file_path, line_re, generate_contents):
    return before_lines(file_path, line_re, generate_contents, 1)

def before_lines(file_path, line_re, generate_contents, n = -1):
    return map_lines(file_path, line_re, lambda line: "%s\n%s" % (generate_contents(line), line), n)

def map_lines(file_path, line_re, g, n = -1):
    def map_lines_action(f, ftemp):
        lines = f.readlines() 
        matching_ixs = find_some(partial(re.search, line_re), lines, n)
        for ix in matching_ixs:
            lines[ix] = g(lines[ix])

        ftemp.writelines(lines)

    return update_file(file_path, map_lines_action)

# creates a new file at the designated path with the provided contents
def new_file(file_path, contents):
    return create_file(file_path, lambda f: f.write(contents))

def rewrite_file(file_path, new_contents):
    return update_file(file_path, lambda _, ftemp: ftemp.write(new_contents)) 

def read_file(file_path, read = lambda f: f.read()): 
    def read_file_action(file_path):
        with open(file_path, 'r') as f:
            return read(f)

    return __crud_action(file_path, read_file_action, __check_file_exists)

# modify(f, ftemp) takes the file object "f" as its first argument (opened with the "read"
# flag) and a temporary file object "ftemp" as its second argument (opened with the "w" flag).
def update_file(file_path, modify):
    def update_file_action(file_path):
        temp_file = file_path + ".tmp"
        with open(file_path, 'r') as f:
            with open(temp_file, 'w') as ftemp:
                modify(f, ftemp)

        os.rename(temp_file, file_path) 

        git('add %s' % file_path)

    return __crud_action(file_path, update_file_action, __check_file_exists)

def create_file(file_path, write_to):
    def check_file_does_not_exist(repo, branch, file_path):
      if os.path.exists(file_path):
        raise Exception("%s already exists in the '%s' branch of '%s'!" % (file_path, branch, repo))

    def create_file_action(file_path):
        with open(file_path, 'w') as f:
            write_to(f)

        git('add %s' % file_path)

    return __crud_action(file_path, create_file_action, check_file_does_not_exist)

def rename_file(old_path, new_path):
    def rename_action(file_path):
        os.rename(file_path, new_path)
        git('add %s' % file_path)
        git('add %s' % new_path)

    return __crud_action(old_path, rename_action, __check_file_exists)

def remove_file(file_path):
    removal_action = lambda _file_path: os.remove(_file_path) or git('rm %s' % _file_path)
    return __crud_action(file_path, removal_action, __check_file_exists) 

def __crud_action(file_path, action, check_action_is_ok):
    def file_action(repo, branch):
        check_action_is_ok(repo, branch, file_path)
        return action(file_path)

    return file_action

# checks if the given file exists
def __check_file_exists(repo, branch, file_path):
    if not os.path.exists(file_path):
        raise Exception("%s does not exist in the '%s' branch of '%s'!" % (file_path, branch, repo))

