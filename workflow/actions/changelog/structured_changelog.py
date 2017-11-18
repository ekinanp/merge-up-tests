from functools import partial
import re

from workflow.constants import VERSION_RE
from workflow.utils import (cmp_version, validate_regex, validate_version)

# Class for changelogs captured by libwhereami and leatherman

VERSION_HEADER = r'##\s+(%s).*$' % VERSION_RE 
VERSION_SECTION = r'###\s+(\w+).*$'
ENTRY_DELIMITERS = r'[\*-]'
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

class ChangelogKey:
    def __init__(self, key_label, key_str): 
        self.matcher = partial(re.match, "^%s$" % key_label)
        self.key_str = key_str

    def match(self, s):
        return self.matcher(s)

# This class represents "simple" CHANGELOGs such as what's found in pxp-agent
# and the cpp-pcp-client.
class StructuredChangelog(object):
    def __init__(self, contents):

    def update(self, version, *changes, **kwargs):

    def render(self):  

