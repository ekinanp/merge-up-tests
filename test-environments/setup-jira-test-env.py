from workflow.jira_service import JiraService

# copy-paste: execfile('setup-jira-test-env.py')

TEST_FILTER = "fixVersion in ('puppet-agent 5.3.3', 'PUP 5.3.3', 'FACT 3.9.3', 'MCO 2.11.4', 'pxp-agent 1.8.1', 'cpp-pcp-client 1.5.5', 'LTH 1.2.2')"

js = JiraService()
