from contextlib import contextmanager
from collections import Iterable
from itertools import (filterfalse, islice)
from functools import reduce
import os
import re
import subprocess

from workflow.constants import VERSION_RE

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

def validate_version(version):
    return validate_regex(VERSION_RE, version, "'%s' is not a valid semantic version!")

@contextmanager
def in_directory(name):
    cwd = os.getcwd()
    os.chdir(name)
    try:
        yield name
    finally:
        os.chdir(cwd)

# Compares two semantic versions

def invert_cmp(cmp_fn):
    return lambda x, y: -cmp_fn(x, y)
#
# TODO: Should just use a python package that already
# has these calculations
def cmp_version(v1, v2):
    def to_tuple(v):
        return tuple([int(vi) for vi in v.split('.')])

    return cmp(to_tuple(v1), to_tuple(v2))

# NOTE: This can probably be removed if we decide to use
# http://gitpython.readthedocs.io/en/stable/
def git(cmd):
    return os.system("git %s" % cmd)

@to_action
def git_action(cmd):
    return git(cmd)

@to_action
def exec_stdout(*argv, **kwargs):
    return subprocess.check_output(argv, **kwargs).strip()

git_head = exec_stdout('git', 'rev-parse', 'HEAD')

@to_action
def push(push_opts = '', prompt_push = None):
    git_push = lambda : git('push %s' % push_opts)

    if not prompt_push:
        git_push()
        return None

    user_response = input("\n\nWould you like to push your changes to 'origin'? ")
    if re.match(r'^(?:y|Y|%s)$' % '|'.join(["%s%s%s" % (l1, l2, l3) for l1 in ['y', 'Y'] for l2 in ['e', 'E'] for l3 in ['s', 'S']]), user_response):
        print("You answered 'Yes'! Pushing your changes to 'origin' ...")
        git_push()
    else:
        print("You answered 'No'! Your changes will not be pushed.")

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

def reverse(xs):
    return xs[::-1]

# const function from Haskell
def const(v):
    return lambda _ : v

# returns the keys of the first n elements of xs satisfying the predicate p
def find_some(p, xs, n = 1):
    filtered_ixs = filter(lambda ix: p(xs[ix]), (e[0] for e in enumerate(xs)))
    if (n >= 0):
        filtered_ixs = islice(filtered_ixs, n)

    return list(filtered_ixs)

# unique takes a comparator function between two elements,
# and a list, and removes all entries where cmp(a, b) == 0.
def unique(compare, xs):
    uxs = []
    for x in xs:
        if not find_some(lambda ux: compare(x, ux) == 0, uxs):
            uxs.append(x)

    return uxs

# takes a bunch of actions together and creates a single action
# out of them.
def sequence(*actions):
    def sequenced_action(*args, **kwargs):
        for do_action in actions:
            do_action(*args, **kwargs)

    return sequenced_action

# partitions an iterator into two halves:
#   (T, F)
# where T contains the elements s.t. pred(x) is True,
# and F are those where pred(x) is False
def ipartition(pred, iterator):
    return (filter(pred, iterator), filterfalse(lambda x : not pred(x), iterator))

def identity(x):
    return x
