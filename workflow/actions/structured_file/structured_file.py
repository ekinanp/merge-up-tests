from workflow.actions.structured_file.section import (Section, section)

class StructuredFile(object):
    def __init__(self, contents, *subsections, **kwargs):
        self.parsed_file = Section("", "(.*)", ".*", *subsections, **kwargs)
        section_stack = [self.parsed_file]

        for line in (line + "\n" for line in contents.splitlines()):
            while(section_stack and not section_stack[-1].process_line(section_stack, line)):
                pass

            if not section_stack:
                break

        while section_stack:
#            print("TOP OF STACK:\n%s" % str(section_stack[-1]))
            cur_section = section_stack.pop()
            cur_section.finish_section()

    def render(self):  
        return self.parsed_file.render()
