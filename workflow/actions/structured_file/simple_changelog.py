from workflow.actions.structured_file.structured_file import StructuredFile
from workflow.actions.structured_file.section import (Section, version_entry, version_entry_ordering_fn, changelog_entry, CHANGELOG_ENTRY_ID_RE)
from workflow.utils import (validate_version, validate_regex)
from workflow.constants import VERSION_RE

CHANGES_SUMMARY_RE = r'([^\s\*][^\*#]*)'

# TODO: Remove this after testing
def o(log_path):
    with open('/Users/enis.inan/GitHub/puppet-agent-workflow/test-changelog/simple/%s' % log_path, 'r') as f:
        return f.read()

# This class represents "simple" CHANGELOGs such as what's found in pxp-agent
# and the cpp-pcp-client.
class SimpleChangelog(StructuredFile):
    def __init__(self, contents):
        super(SimpleChangelog, self).__init__(contents, version_entry(changelog_entry), ordering_fn = version_entry_ordering_fn)

    # For kwargs, if adding in changes for a new version, then pass in an entry into the
    # "summary" field. This is required.
    @validate_version(1)
    @validate_regex(CHANGES_SUMMARY_RE, 'summary')
    def update(self, version, *changes):
        entry_sections = [Section.from_header_str("* %s" % change, CHANGELOG_ENTRY_ID_RE) for change in changes]
        version_entry = self.parsed_file[version]
        if version_entry:
            version_entry.insert_subsections(*entry_sections)
            return

        summary = kwargs.get('summary')
        if not summary:
            raise Exception("When creating a new set of changes for a new version, you must provide a summary of the nature of these changes!")

        entry_sections[0].header_str += "\n"
        version_section = Section.from_header_str("## %s\n\n%s\n" % (version, summary), VERSION_RE, *entry_sections)
        self.parsed_file.insert_subsections(version_section)
