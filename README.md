# puppet-agent-workflow
This repo contains code for a mini-DSL that can be used to simulate/automate a simple git workflow.
"Work" inside a git repo is carried out within a branch, and each unit of work is called an
"action". Here, an "action" is a function that takes in the repository basename (e.g. 'facter'),
and the branch that's currently being operated on. It then does something inside that branch.
There are all types of actions in this repo, most of which are found in the workflow/actions
directory. Example actions include:

* file-specific actions, such as sed-like substitution on a single line, or inserting/adding content before/after certain lines in a file. These actions take the file-path as the first parameter, where the file-path can either be an absolute path or relative to the repository's working directory (e.g. "CHANGELOG.md"). See workflow/actions/file\_actions.py for more info.

* repository-specific actions. These are actions common to any git repository. Examples include version bumps, updating changelogs, updating component.json files for vanagon repos, etc. See workflow/actions/repo\_actions.py for more info.

## GitRepository
This class represents any fork of a puppetlabs git repository. To create an instance of this object, the user must provide the following parameters:
* repo\_name representing the repository's basename
* branches representing all the relevant branches that will be modified
* github\_user representing the specific fork that will be operated on
* workspace representing the root directory where all repositories will be stored
* metadata, captured in \*\*kwargs. This includes information such as whether the repository has a CHANGELOG and if so, what type; whether the repository can be version bumped, and whether the repository is a vanagon repo. See workflow/repos/pxp\_agent.py for example, or workflow/repos/puppet\_agent.py for how these parameters are passed in.

At a high level, the code will clone the repo from scratch if it does not already exist, and then "reset" each of the passed in branches so that they are synchronized with their upstream counterparts. This effectively creates a clean slate for the branches to start from. If the repo does exist, the constructor will not do anything.

There are three key methods in this class:
* in\_repo. This routine takes in a single action, represented as a no-argument procedure, and executes it, returning its value to the user. This routine is useful if you cannot do something inside a git branch (e.g. because you're trying to resolve a merge conflict)
* in\_branch is like in\_repo, except the action operates inside a specific branch
* to\_branch is the same as in\_branch, except it takes zero or more actions, executes them, and does not return a result. It then pushes whatever changes these actions made up to the remote fork.

For the DSL, to\_branch is what will be most commonly used. A short-cut has been provided by overriding the "[]" operator to take a branch as its key and serve as a wrapper to this method. That way, code such as:

facter["3.6.x"](<br>
&nbsp;&nbsp;&nbsp;&nbsp;modify_line("locales/FACTER.pot", ...),<br>
&nbsp;&nbsp;&nbsp;&nbsp;bump_version("10.12.13"),<br>
&nbsp;&nbsp;&nbsp;&nbsp;create_file("new_feature", "contents"),<br>
&nbsp;&nbsp;&nbsp;&nbsp;commit("Also created a new file"),<br>
&nbsp;&nbsp;&nbsp;&nbsp;...<br>
)<br>

can be executed. This is equivalent to:<br><br>
facter.to\_branch(<br>
&nbsp;&nbsp;&nbsp;&nbsp;"3.6.x",<br>
&nbsp;&nbsp;&nbsp;&nbsp;modify_line(...),<br>
&nbsp;&nbsp;&nbsp;&nbsp;bump_version(...),<br>
&nbsp;&nbsp;&nbsp;&nbsp;create_file(...),<br>
&nbsp;&nbsp;&nbsp;&nbsp;commit(...),<br>
&nbsp;&nbsp;&nbsp;&nbsp;...<br>
)<br>

NOTE: The naming is a bit poor and it's something that should eventually be changed. For now, to\_branch should only be called when you will actually be modifying a repo (by, e.g. modifying an existing file, reverting a commit, etc.) and you want these changes to be pushed. Otherwise, in\_branch should be called.

NOTE: Finally, notice that when doing repo[branch-name], what's actually pushed/modified is the stub of that branch, which is generated in the \_\_stub\_branch routine of the GitRepository class. Currently, it prepends a prefix to the branch so that when you do:

facter\["3.6.x"\](new\_file("foo", "bar"), commit("Created a new file!"))

Changes will actually be made and pushed up to "{BRANCH-PREFIX}-3.6.x". This can be overridden when necessary.

## Component
This class represents components of a vanagon repo, found in configs/components. These are git repositories, the only difference is that they automatically initialize their vanagon repo's corresponding component.json file's URL and REF to point to the forked url and the HEAD ref, respectively. They also update the component.json file's REF automatically whenever something is pushed up to them. See workflow/repos/facter.py for an example of how a component is initialized.

## Merge-Conflict Scenarios
These are found in the merge-conflicts folder, specifically the conflict\_generators.py file. Currently, only the following scenarios are created based on comments in PA-1704:
* Component JSON conflicts
* Version bump conflicts
* Changelog conflicts (for Leatherman only, others can be added when needed)
* POT file metadata conflicts

Given the nature of the DSL, other conflicts can be created when needed without too much difficulty.

## Examples
Look at the files in test-scripts to see some examples of how to use the DSL.
