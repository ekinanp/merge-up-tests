import os

import utils

_path = os.path

# This module contains some useful functions that are used to create actions capturing
# CRUD operations on files (save for the "R" part). These actions only make sense on a
# GitRepository object
#
# Using the functions here, we can write things like
#   facter.in_branch(
#     '3.6.x',
#     "Updating stuff!",
#     update_file('Makefile', <code here>),
#     create_file('some feature', <code here>)
#   ) 
#
# Each "action" should take the repo name and the branch as parameters (to provide
# clearer error messages on what might go wrong). 

def update_file(file_path, modify, open_flag = 'a'):
    return __cu_action(file_path, modify, __check_file_exists, open_flag)

def create_file(file_path, write_to):
    def check_file_does_not_exist(repo, branch, file_path):
      if not _path.exists(file_path):
        raise Exception("%s already exists in the '%s' branch of '%s'!" % (file_path, branch, repo))

    return __cu_action(file_path, write_to, check_file_does_not_exist, 'w')

def remove_file(file_path):
    return __crud_action(file_path, os.remove, __check_file_exists) 

# Short for "create" OR "update" action
def __cu_action(file_path, action, check_action_is_ok, open_flag):
    def crud_action(file_path):
        with open(file_path, open_flag) as f:
            action(f)

        return "add"

    return __crud_action(file_path, crud_action, check_action_is_ok)

def __crud_action(file_path, action, check_action_is_ok):
    def file_action(repo, branch):
        check_action_is_ok(file_path, repo, branch)
        result = action(file_path)
        git('%s %s' % (result, file_path))

    return file_action

def __check_file_exists(repo, branch, file_path):
    if not _path.exists(file_path):
        raise Exception("%s does not exist in the '%s' branch of '%s'!" % (file_path, branch, repo))
