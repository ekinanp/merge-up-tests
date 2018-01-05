from workflow.utils import unique

from jira import JIRA
from hypchat import HypChat
import os
import re

# TODO: Maybe rename this class to something more generic, like Atlassian? Reason is that
# the class does not just query the Jira API, but also the HipChat API. I chose Jira here
# for now since when we do query ticket info., we also return HipChat info. as well
class JiraService:
    def __init__(self):
        self.jira = JIRA(server=os.environ['JIRA_INSTANCE'], basic_auth=(os.environ['JIRA_USER'], os.environ['JIRA_PASSWORD']))
        self.hipchat = HypChat(os.environ['HIPCHAT_TOKEN'], endpoint = "https://puppet.hipchat.com")

        # map of <field-id> -> <field-name>, used to make querying custom fields more readable.
        self.name_map = {field['id'] : field['name'] for field in self.jira.fields()}

    # applies the passed-in JQL filter and returns an array of tickets that match it
    def get_tickets(self, search_filter):
        def process_ticket(ticket):
            ticket_fields = self.get_fields(ticket)
            return {
                "ticket" : ticket.key,
                "status" : ticket_fields["Status"]["name"]
            }

        return [process_ticket(ticket) for ticket in self.jira.search_issues(search_filter)]

    # returns a dictionary with the following keys:
    #   (1) involved_devs
    #         Nested structure with the following keys:
    #            -Everything that dev_info returns
    #            -category (Either "Assignee", "Watcher", or "Reporter", in that order)
    #   (2) team
    #         Lists the team associated with the ticket
    #
    # NOTE: Some puppet employees might have their e-mails end in @puppetlabs.com instead of
    # @puppet.com -- if this happens, then the code should be modified to try both e-mails when
    # acquiring the dev info.
    #
    # TODO: What if ticket does not have a field? E.g. No team, no assignee, etc. Handle this
    # case!
    def ticket_info(self, ticket):
        def involved_dev_info(involved_dev, category):
            dev_info = self.dev_info("%s@puppet.com" % involved_dev['key'])
            dev_info['category'] = category
            return dev_info

        ticket_info = self.get_fields(self.jira.issue(ticket))
        ticket_watchers = self.jira.watchers(ticket)

        # calculate the involved devs
        (assignee, reporter) = tuple(
            [[involved_dev_info(ticket_info[dev_type], dev_type)] if ticket_info[dev_type] else [] for dev_type in ("Assignee", "Reporter")]
        )
        watchers = [involved_dev_info(watcher.raw, "Watcher") for watcher in ticket_watchers.watchers]
        return {
            "involved_devs" : assignee + watchers + reporter,
            "team" : ticket_info["Team"]["value"] if ticket_info["Team"] else None
        }

    # returns a dictionary with the following keys:
    #   (1) name
    #   (2) email
    #   (3) hipchat_alias
    def dev_info(self, dev_email):
        hipchat_info = self.hipchat.get_user(dev_email)
        return {
            'name' : hipchat_info['name'],
            'email' : dev_email,
            'hipchat_alias' : hipchat_info['mention_name']
        }

    # TODO: Make this private after everything's tested
    def get_fields(self, jira_issue):
        return {self.name_map[field_id] : field_value for field_id, field_value in jira_issue.raw['fields'].items()}
