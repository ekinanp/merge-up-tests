import os
import re

from utils import git

_path = os.path

# This module contains some useful functions that are used to create actions capturing
# CRUD operations on files (save for the "R" part). These actions only make sense on a
# GitRepository object
#
# Using the functions here, we can write things like
#   facter.in_branch(
#     '3.6.x',
#     update_file('Makefile', <code here>),
#     create_file('some feature', <code here>),
#     commit("Doing stuff!")
#   ) 
#
# Each "action" should take the repo name and the branch as parameters (to provide
# clearer error messages on what might go wrong). 

# replaces the first occurrence of the line matching line_re with
# the substitution pattern
def replace_line(file_path, line_re, substitution):
    def replace_line_action(f, ftemp):
        found_match = False
        for line in f:
            line = line.rstrip()
            if not found_match:
                new_line = re.sub(line_re, substitution, line)
                found_match = new_line != line
                line = new_line

            ftemp.write("%s\n" % line)

        return "add"

    return update_file(file_path, replace_line_action)

# creates a new file at the designated path with the provided contents
def new_file(file_path, contents):
    return create_file(file_path, lambda f: f.write(contents))

# modify(f, ftemp) takes the file object "f" as its first argument (opened with the "read"
# flag) and a temporary file object "ftemp" as its second argument (opened with the "w" flag).
def update_file(file_path, modify):
    def update_file_action(file_path):
        temp_file = file_path + ".tmp"
        with open(file_path, 'r') as f:
            with open(temp_file, 'w') as ftemp:
                modify(f, ftemp)

        os.rename(temp_file, file_path) 

        return "add"

    return __crud_action(file_path, update_file_action, __check_file_exists)

def create_file(file_path, write_to):
    def check_file_does_not_exist(repo, branch, file_path):
      if _path.exists(file_path):
        raise Exception("%s already exists in the '%s' branch of '%s'!" % (file_path, branch, repo))

    def create_file_action(file_path):
        with open(file_path, 'w') as f:
            write_to(f)

        return "add"

    return __crud_action(file_path, create_file_action, check_file_does_not_exist)

def remove_file(file_path):
    removal_action = lambda _file_path: os.remove(_file_path) or "rm"
    return __crud_action(file_path, removal_action, __check_file_exists) 

def __crud_action(file_path, action, check_action_is_ok):
    def file_action(repo, branch):
        check_action_is_ok(repo, branch, file_path)
        result = action(file_path)
        git('%s %s' % (result, file_path))

    return file_action

def __check_file_exists(repo, branch, file_path):
    if not _path.exists(file_path):
        raise Exception("%s does not exist in the '%s' branch of '%s'!" % (file_path, branch, repo))
