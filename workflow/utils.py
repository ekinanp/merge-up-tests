from contextlib import contextmanager
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
