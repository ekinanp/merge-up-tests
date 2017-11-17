import re

from workflow.constants import VERSION_RE
from workflow.utils import (cmp_version, validate_regex, validate_version)

VERSION_HEADER = r'##\s+(%s)' % VERSION_RE 
CHANGES_SUMMARY = r'([^\s\*][^\*#]*)'

# The "\[(?:#)?[^\]]+\]" is a regex describing the issue/ticket no. (label)
# associated with the entry, while the "[^\*#]+" part is the entry's
# content. Thus, we can read this as:
#   CHANGELOG_ENTRY = '\*\s+(LABEL<OR>CONTENT)CONTENT'
# where if there is no label, it will look just for the content. Otherwise,
# if there is a label it will get that and then the content.
CHANGELOG_ENTRY = r'\*\s+((?:\[(?:#)?[^\]]+\]|[^\*#]+)[^\*#]+)'

VERSION_ENTRIES =r'%s\s+%s\s+((?:%s)*)' % (VERSION_HEADER, CHANGES_SUMMARY, CHANGELOG_ENTRY)

# TODO: Remove this after testing
def o(log_path):
    with open('/Users/enis.inan/GitHub/puppet-agent-workflow/test-changelog/simple/%s' % log_path, 'r') as f:
        return f.read()

# This class represents "simple" CHANGELOGs such as what's found in pxp-agent
# and the cpp-pcp-client.
class SimpleChangelog(object):
    def __init__(self, contents):
        def parse_version_entry(parsed_results, version_entry):
            (version, changes_summary, changelog_entries) = re.match(VERSION_ENTRIES, version_entry, re.M).groups()[0:3]

            parsed_results[version.strip()] = (changes_summary.strip(), map(lambda xs: xs.strip(), re.findall(CHANGELOG_ENTRY, changelog_entries, re.M)))
            return parsed_results

        version_changes = [version_change[0] for version_change in re.findall(VERSION_ENTRIES.join(['(', ')']), contents, re.M)]
        self.changelog = reduce(parse_version_entry, version_changes, {})

    # For kwargs, if adding in changes for a new version, then pass in an entry into the
    # "summary" field. This is required.
    @validate_version(1)
    @validate_regex(CHANGES_SUMMARY, 'summary')
    def update(self, version, *changes, **kwargs):
        version_entry = self.changelog.get(version)
        if version_entry:
            self.changelog[version] = (version_entry[0], list(changes) + version_entry[1])
            return

        summary = kwargs.get('summary')
        if not summary:
            raise Exception("When creating a new set of changes for a new version, you must provide a summary of the nature of these changes!")

        self.changelog[version] = (summary, changes)

    def render(self):  
        def render_entry((version, (summary, version_entries))):
            rendered_version_entries = '\n'.join(["* %s" % version_entry for version_entry in version_entries]) 
            if rendered_version_entries:
                rendered_version_entries += "\n"

            return '\n\n'.join(['## %s' % version, summary, rendered_version_entries])

        sorted_parsed_results = sorted(self.changelog.iteritems(), cmp = lambda e1, e2: cmp_version(e1[0], e2[0]), reverse = True)

        return '\n'.join([render_entry(e) for e in sorted_parsed_results])
