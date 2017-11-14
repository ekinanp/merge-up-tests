# puppet-agent-workflow
This repo holds scripts that can be used to simulate an actual workflow involving the puppet-agent itself. These include things like:
  (1) Updating either the puppet-agent repo itself or one of its components
  (2) Creating merge-up conflicts to test
 
This will be expanded upon as more and more pieces of the puppet-agent release process are automated so that these automated parts can be thoroughly tested to ensure that they are correct.

# TODO:
The planned structure is like this:

GitRepository
  PuppetAgent
  Component
    Facter
    Puppet
    Leatherman
    ...

But this is still a WIP. Might be good to put the repo stuff in a "repos" directory. Still
undecided on this, however
