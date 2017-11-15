from contextlib import contextmanager
from collections import Iterable
import os
import subprocess

# decorator that converts a function to an action that can be used with
# the in_branch routine of git_repository
def to_action(f):
    return lambda *args, **kwargs: lambda repo_name, branch: f(*args, **kwargs)

@contextmanager
def in_directory(name):
    cwd = os.getcwd()
    os.chdir(name)
    yield name
    os.chdir(cwd)

# NOTE: This can probably be removed if we decide to use
# http://gitpython.readthedocs.io/en/stable/
def git(cmd):
    return os.system("git %s" % cmd)

@to_action
def git_action(cmd):
    return git(cmd)

@to_action
def exec_stdout(*argv):
    return subprocess.check_output(argv).strip()

# creates a commit action
def commit(msg):
    return git_action('commit -m \"%s\"' % msg)

# flattens nested lists into a single list
def flatten(xss):
    if not isinstance(xss, Iterable) or isinstance(xss, str):
        return [xss]

    return reduce(lambda accum, x: accum + flatten(x), xss, [])

# takes a bunch of actions together and creates a single action
# out of them.
#
# TODO: With the implementation of "flatten" above, this routine
# can maybe be removed. But this is not that important
def sequence(*actions):
    def sequenced_action(repo_name, branch):
        for do_action in actions:
            do_action(repo_name, branch)

    return sequenced_action
