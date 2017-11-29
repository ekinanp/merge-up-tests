# puppet-agent-workflow
This repo contains code for a mini-DSL that can be used to simulate/automate a simple git workflow.
"Work" inside a git repo is carried out within a branch, and each unit of work is called an
"action". Here, an "action" is a function that takes in the repository basename (e.g. 'facter'),
and the branch that's currently being operated on. It then does something inside that branch.
There are all types of actions in this repo, most of which are found in the `workflow/actions`
directory. Example actions include:

* file-specific actions, such as sed-like substitution on a single line, or inserting/adding content before/after certain lines in a file. These actions take the file-path as the first parameter, where the file-path can either be an absolute path or relative to the repository's working directory (e.g. "CHANGELOG.md"). See `workflow/actions/file_actions.py` for more info.

* repository-specific actions. These are actions common to any git repository. Examples include version bumps, updating changelogs, updating component.json files for vanagon repos, etc. See `workflow/actions/repo_actions.py` for more info.

## Setup
You must have Python 2 installed in order to run the code in this repo.

This script does not depend on any external python packages. All one has to do is set

`PYTHONPATH=<project-root>:${PYTHONPATH}`

in `~/.bash\_profile`. On my machine, `<project-root> = /Users/enis.inan/GitHub/puppet-agent-workflow`. Then you can do:

`python test_scripts/<script-name>`

to run one of the example scripts.

## GitRepository
This class represents any fork of a puppetlabs git repository. To create an instance of this object, the user must provide the following parameters:
* `repo_name` representing the repository's basename
* `branches` representing all the relevant branches that will be modified
* `github_user` representing the specific fork that will be operated on

Note that the `github_user` is set to a default value, which is the value of the environment variable `GITHUB_USERNAME`.

One can also pass in the following keyword arguments:
* `workspace` which specifies the directory that the repository resides in. If this is not provided, then a temporary directory will be created, whose value can be retrieved by referencing the `workspace` field of the GitRepository object.
* `stub_branch`, a function that takes in a git branch name and returns a "stubbed" version of this branch. This way, changes made to a "raw" branch (represented by a branch in the "branches" parameter above) will actually be made to the "stubbed" version of that branch. If you do not want to stub any branches, this can be the identity function. Note that if stub\_branch is not provided, then the stubbing function is f(branch) = kwargs[stub\_prefix] + "-" + branch. If stub\_prefix is not provided, then a constant `BRANCH_PREFIX` value is used instead.
* `metadata`. This should be a dictionary. It includes information such as whether the repository has a CHANGELOG and if so, what type; whether the repository can be version bumped, and whether the repository is a vanagon repo. See `workflow/repos/pxp_agent.py` for example, or `workflow/repos/puppet_agent.py`.

At a high level, the code will clone the repo from scratch if it does not already exist using the ssh git URLs. If you would like to start from a clean slate, then invoke the `reset_branches()` method or the `reset_branch` routine for an individual branch -- these routines synchronize the passed in branches to their upstream counterparts.

There are three key methods in this class:
* `in_repo`. This routine takes in a single action, represented as a no-argument procedure, and executes it, returning its value to the user. This routine is useful if you cannot do something inside a git branch (e.g. because you're trying to resolve a merge conflict)
* `in_branch` is like in\_repo, except the action operates inside a specific branch
* `to_branch` is the same as in\_branch, except it takes zero or more actions, executes them, and does not return a result. It then pushes whatever changes these actions made up to the remote fork by default. If the user would like to be prompted before having their changes pushed, then they can pass in a truthy value for the prompt\_push keyword argument. Here, changes are only pushed if the user enters "y", "Y", or some cased form of "yes".

For the DSL, `to_branch` is what will be most commonly used. A short-cut has been provided by overriding the `[]` operator to take a branch as its key and serve as a wrapper to this method. That way, code such as:

```
facter["3.6.x"](
    modify_line("locales/FACTER.pot", ...),
    bump_version("10.12.13"),
    new_file("new_feature", "contents"),
    commit("Also created a new file"),
    ...
)
```

can be executed. This is equivalent to:

```
facter.to_branch(
    "3.6.x",
    modify_line(...),
    bump_version(...),
    create_file(...),
    commit(...),
    ...
)
```

An example of a prompted push is below:

```
facter["3.6.x"](
    new_file("new_feature", "contents"),
    commit("Also created a new file"),
    prompt_push = True
)
```

NOTE: The naming is a bit poor and it's something that should eventually be changed. For now, `to_branch` should only be called when you will actually be modifying a repo (by, e.g. modifying an existing file, reverting a commit, etc.) and you want these changes to be pushed. Otherwise, `in_branch` should be called.

NOTE: Again, remember that when doing `repo[branch-name]`, what's actually pushed/modified is the stub of that branch that is determined by the stubbing function (call it `stub` for readability). By default, the stubbing function prepends the branch with a prefix; one can pass in their own stubbing function via. the `stub_branch` keyword argument. For example, 

`facter["3.6.x"](new_file("foo", "bar"), commit("Created a new file!"))`

Changes will actually be made and pushed up to `stub("3.6.x")`.

## Component
This class represents components of a vanagon repo, found in configs/components. These are git repositories, the only difference is that they automatically initialize their vanagon repo's corresponding component.json file's URL and REF to point to the forked url and the HEAD ref, respectively. They also update the component.json file's REF automatically whenever something is pushed up to them. See `workflow/repos/facter.py` for an example of how a component is initialized.

## Merge-Conflict Scenarios
These are found in the merge-conflicts folder, specifically the conflict\_generators.py file. Currently, only the following scenarios are created based on comments in PA-1704:
* Component JSON conflicts
* Version bump conflicts
* Changelog conflicts (for Leatherman only, others can be added when needed)
* POT file metadata conflicts

Given the nature of the DSL, other conflicts can be created when needed without too much difficulty.

## Examples
Look at the files in test\_scripts to see some examples of how to use the DSL.
