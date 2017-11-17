from contextlib import contextmanager
from collections import Iterable
from itertools import (ifilter, islice)
import os
import re
import subprocess

from constants import VERSION_RE

# decorator that converts a function to an action that can be used with
# the in_branch routine of git_repository
def to_action(f):
    return lambda *args, **kwargs: lambda repo_name, branch: f(*args, **kwargs)

# Decorator to check that some argument of the routine is valid
# using a user-provided validation function. If the check
# fails, then an exception is thrown. Note that if key is an integer,
# then the input in args[key] will be checked. Otherwise, the input in
# kwargs[key] will be looked at, if the user provided it. Note that if
# the argument does not exist, then this decorator will pass-thru to
# f.
def validate_input(valid, key, error_msg = "Input %s is invalid!"):
    def validate_input_decorator(f):
        def with_validate_input(*args, **kwargs):
            obj = args if isinstance(key, int) else kwargs
            try:
                s = obj[key]
            except Exception:
                return f(*args, **kwargs)

            if not valid(s):
                raise Exception(error_msg % s)

            return f(*args, **kwargs)
        
        return with_validate_input

    return validate_input_decorator

def validate_regex(regex, key, error_msg = None):
    if not error_msg:
        error_msg = "Input %s does not conform to the passed-in regex '{_regex}'!".format(_regex = regex)

    return validate_input(lambda s: re.match(regex, s), key, error_msg)

def validate_version(key):
    return validate_regex(VERSION_RE, key, "'%s' is not a valid semantic version!")

def validate_presence(collection, key, error_msg = None):
    if not error_msg:
        error_msg = "The passed in key, '%s', is not present in this collection!"

    def contains(key):
        try:
            collection[key]
            return True
        except:
            return False

    return validate_input(contains, key, error_msg)

@contextmanager
def in_directory(name):
    cwd = os.getcwd()
    os.chdir(name)
    yield name
    os.chdir(cwd)

# Compares two semantic versions
#
# TODO: Should just use a python package that already
# has these calculations
def cmp_version(v1, v2):
    return cmp(v1.split('.'), v2.split('.'))

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

@to_action
def noop_action():
    pass

# flattens nested lists into a single list
def flatten(xss):
    if not isinstance(xss, Iterable) or isinstance(xss, str):
        return [xss]

    return reduce(lambda accum, x: accum + flatten(x), xss, [])

# const function from Haskell
def const(v):
    return lambda _ : v

# returns the keys of the first n elements of xs satisfying the predicate p
def find_some(p, xs, n = 1):
    filtered_ixs = ifilter(lambda ix: p(xs[ix]), (e[0] for e in enumerate(xs))) 
    if (n >= 0):
        filtered_ixs = islice(filtered_ixs, n)

    return list(filtered_ixs)

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
