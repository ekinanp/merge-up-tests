from workflow.actions.file_actions import (after_line, new_file)
from workflow.repos.puppet_agent import PuppetAgent
from workflow.repos.puppet import Puppet
from workflow.repos.leatherman import Leatherman
from workflow.repos.facter import Facter 
from workflow.repos.pxp_agent import PxpAgent
from workflow.repos.cpp_pcp_client import CppPcpClient
from workflow.repos.libwhereami import Libwhereami
from workflow.repos.hiera import Hiera 
from workflow.repos.marionette_collective import MarionetteCollective
from workflow.utils import (const, commit)

WORKSPACE="/Users/enis.inan/GitHub/puppet-agent-workflow/localization-tests"
BRANCH_PREFIX = "localization-tests" 

puppet_agent = PuppetAgent(workspace = WORKSPACE, stub_prefix = BRANCH_PREFIX)
puppet_agent.reset_branch("master")

def setup_puppet():
    puppet = Puppet(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_prefix = BRANCH_PREFIX)
    puppet.reset_branch("master")
    puppet["master"](
        after_line("lib/puppet/resource.rb", r"_\('", const("%smsg2 = _('Some dummy message for POT generation!')" % (" " * 4))),
        commit("Setting up a test environment for POT file generation!")
    )

def setup_leatherman():
    leatherman = Leatherman(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_prefix = BRANCH_PREFIX)
    leatherman.reset_branch("master")
    leatherman["master"](
        after_line("curl/src/client.cc", r"throw http_exception\(_\(\"failed to create cURL handle.\"\)\)", const("%s_(\"BLAH MESSAGE FOR TRANSLATION\")" % (" "*12))),
        commit("Setting up a test environment for POT file generation!")
    )

def setup_pxp_agent():
    pxp_agent = PxpAgent(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_prefix = BRANCH_PREFIX)
    pxp_agent.reset_branch("master")
    pxp_agent["master"](
        after_line("lib/src/modules/task.cc", r"Downloading the task file from the master-uri", const("%sLOG_WARNING(\"BLAH MESSAGE FOR TRANSLATION\")" % (" "*14))),
        commit("Setting up a test environment for POT file generation!")
    )

def setup_cpp_pcp_client():
    cpp_pcp_client = CppPcpClient(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_prefix = BRANCH_PREFIX)
    cpp_pcp_client.reset_branch("master")
    cpp_pcp_client["master"](
        after_line("lib/src/connector/connection.cc", r"WebSocket in 'connecting' state", const("%sLOG_WARNING(\"BLAH MESSAGE FOR TRANSLATION\")" % (" "*12))),
        commit("Setting up a test environment for POT file generation!")
    )

def setup_libwhereami():
    libwhereami = Libwhereami(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_prefix = BRANCH_PREFIX)
    libwhereami.reset_branch("master")
    libwhereami["master"](
        after_line("lib/src/sources/lparstat_source.cc", r"lparstat executable not found", const("%sLOG_WARNING(\"BLAH MESSAGE FOR TRANSLATION\")" % (" "*12))),
        commit("Setting up a test environment for POT file generation!")
    )

def setup_mcollective():
    mcollective = MarionetteCollective(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_prefix = BRANCH_PREFIX)
    mcollective.reset_branch("master")
    mcollective["master"](
        new_file("some_random_file", "some random contents"),
        commit("Creating some random commit to test the localization noop job!")
    )

def setup_facter():
    facter = Facter(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_prefix = BRANCH_PREFIX)
    facter.reset_branch("master")
    facter["master"](
            after_line("lib/src/logging/logging.cc", r"log\(level::warning", const("%slog(level::warning, \"BLAH MESSAGE FOR TRANSLATION\")" % (" "*16))),
        commit("Setting up a test environment for POT file generation!")
    )

def setup_other(component_type, branch):
    component = component_type(workspace = WORKSPACE, puppet_agent = puppet_agent, stub_prefix = BRANCH_PREFIX)
    component.reset_branch("master")

def setup_bump_component():
    puppet_agent.reset_branch("master")
    setup_leatherman()

#setup_puppet()
#setup_leatherman()
#setup_pxp_agent()
#setup_cpp_pcp_client()
#setup_libwhereami()
#setup_mcollective()
#setup_facter()
setup_other(Hiera, "master")

