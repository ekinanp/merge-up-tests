from contextlib import contextmanager
from collections import Iterable
import os

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

# creates a commit action
def commit(msg):
    return lambda repo_name, branch: git('commit -m \"%s\"' % msg)

# flattens nested lists into a single list
def flatten(xss):
    if not isinstance(xss, Iterable) or isinstance(xss, str):
        return [xss]

    return reduce(lambda accum, x: accum + flatten(x), xss, [])

# takes a bunch of actions together and creates a single action
# out of them.
def sequence(*actions):
    def sequenced_action(repo_name, branch):
        for do_action in actions:
            do_action(repo_name, branch)

    return sequenced_action
