from workflow.actions.structured_file.structured_file import StructuredFile
from workflow.actions.structured_file.section import (Section, version_entry, version_entry_ordering_fn, changelog_subsection, changelog_entry, CHANGELOG_ENTRY_ID_RE)
from workflow.utils import (validate_version, validate_regex, reverse)
from workflow.constants import VERSION_RE

# TODO: Remove this after testing
def o(log_path):
    with open('/Users/enis.inan/GitHub/puppet-agent-workflow/test-changelog/sectioned/%s' % log_path, 'r') as f:
        return f.read()

# This class represents more complicated, sectioned changelogs such as what is found
# in Leatherman and Libwhereami
class SectionedChangelog(StructuredFile):
    def __init__(self, contents, *subsection_headers):
        super(SectionedChangelog, self).__init__(
            contents,
            version_entry(*[changelog_subsection(header) for header in subsection_headers]),
            ordering_fn = version_entry_ordering_fn
        )

    # Note that each element in "changes" should be of the form:
    #    'subsection_header' => [changelog_entries]
    # 
    # TODO: Refactor this code to remove the "if subsection then blah" pattern,
    # as it also appears in SimpleChangelog. Probably should be something that
    # belongs in the "Section" class. It is a bit annoying to read here.
    @validate_version(1)
    def update(self, version, *changes):
        # make the entry sections first
        def add_entries(accum, entries):
            header = entries.keys()[0]
            accum[header] = accum.get(header, []) + reverse(entries[header])
            return accum

        merged_entries = reduce(add_entries, changes, {})
        
        version_entry = self.parsed_file[version]
        if not version_entry:
            version_entry = Section.from_header_str("## [%s]\n" % version, VERSION_RE)
            self.parsed_file.insert_subsections(version_entry)
        
        for header in merged_entries:
            header_entry = version_entry[header]
            trailing_newline = ""
            if not header_entry:
                header_entry = Section.from_header_str("### %s\n" % header, "(%s)" % header)
                version_entry.insert_subsections(header_entry)
                trailing_newline = "\n"

            entry_sections = [Section.from_header_str("- %s" % change, CHANGELOG_ENTRY_ID_RE) for change in merged_entries[header]]
            entry_sections[0].header_str += trailing_newline
            header_entry.insert_subsections(*entry_sections)

def update_section(section_name):
    return lambda *changes: {section_name: list(changes)}
