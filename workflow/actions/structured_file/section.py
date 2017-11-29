from functools import partial
import re

from workflow.utils import (find_some, unique, invert_cmp, cmp_version)
from workflow.constants import VERSION_RE

# TODO: Could maybe refactor so that the parsed_subsections would be a tuple of the
# form: (subsection, post) where "post" would capture stuff between one subsection
# and another. But this is more complexity, so only do it if it needs to be done
#
class Section:
    @staticmethod
    def same_section(s1, s2):
        return s1.section_id == s2.section_id

    @classmethod
    def from_header_str(cls, header_str, section_id_re, *subsections, **kwargs):
        new_section = cls(header_str + "\n", r"(%s)" % section_id_re, "", **kwargs)
        new_section.insert_subsections(*subsections)
        new_section.finish_section()
        return new_section

    def __init__(self, starting_line, section_id_re, header_str_re, *subsections, **kwargs):
        self.header_str = starting_line
        self.section_id_re = section_id_re
        self.header_str_re = header_str_re
        self.subsections = subsections
        self.parsed_subsections = []
        self.ordering_fn = kwargs.get('ordering_fn')

    def append_subsection(self, subsection):
        self.parsed_subsections.append(subsection)

    def insert_subsections(self, *subsections):
        for subsection in subsections:
            self.parsed_subsections.insert(0, subsection)

        self.__sort_subsections()

    def process_line(self, section_stack, line):
        top = section_stack[-1]
        if (top != self):
            raise Exception("This is not the current context.")

        for start_subsection in self.subsections:
            if start_subsection(section_stack, line):
                return True

        if not re.match(self.header_str_re, line):
            section_stack.pop()
            self.finish_section()
            return False

        self.header_str += line
        return True

    def finish_section(self):
        self.section_id = re.search(self.section_id_re, self.header_str).group(1)

        # Ensure that the subsections are unique
        unique_subsections = unique(lambda s1, s2: not Section.same_section(s1, s2), self.parsed_subsections)
        if len(unique_subsections) != len(self.parsed_subsections):
            raise Exception("All sub-sections of the current section '%s' must have unique section ids!" % self.section_id)

    def __sort_subsections(self):
        if self.ordering_fn:
            self.parsed_subsections.sort(cmp = self.ordering_fn)

    def render(self):
        return self.header_str + ''.join([subsection.render() for subsection in self.parsed_subsections])

    def __getitem__(self, subsection_id):
        subsection = find_some(lambda subsection: subsection.section_id == subsection_id, self.parsed_subsections)
        if not subsection:
            return None

        return self.parsed_subsections[subsection[0]]

    # For testing purposes
    def __str__(self):
        return self.pretty_print(0)

    def pretty_print(self, indent = 0):
        indentation = '=' * indent

        printed_attribute = self.section_id if hasattr(self, 'section_id') else self.header_str

        return "\n".join([
             indentation + "ROOT: " + printed_attribute,
             '\n'.join([subsection.pretty_print(indent + 4) for subsection in self.parsed_subsections]),
        ])

def section(header_start_re):
    def section_decorator(make_section):
        def start_section(section_stack, line):
            if not re.match(header_start_re, line):
                return False

            new_section = make_section(line)
            section_stack[-1].append_subsection(new_section)
            section_stack.append(new_section)
            return True

        return start_section

    return section_decorator

def version_entry(*subsections):
    @section("##")
    def version_section(line):
        return Section(line, r"(%s)" % VERSION_RE, "(?:[^#]|\s).*", *subsections)

    return version_section

def version_entry_ordering_fn(s1, s2):
    return invert_cmp(cmp_version)(s1.section_id, s2.section_id)

CHANGELOG_ENTRY_ID_RE = r'([^-\*\s].*)'

@section(r'\s*(?:-|\*)')
def changelog_entry(line):
    return Section(line, CHANGELOG_ENTRY_ID_RE, r'[^-\*#]+')

def changelog_subsection(name, entry_type = changelog_entry):
    @section("### %s" % name)
    def make_changelog_subsection(line):
        return Section(line, r'(%s)' % name, "\s+", entry_type)

    return make_changelog_subsection
