from functools import partial
import re

from workflow.constants import VERSION_RE
from workflow.utils import (find_some)

class Context:
    def __init__(self, starting_line, rest_re, *context_creators):
        self.root_str = starting_line
        self.rest_re = rest_re
        self.context_creators = context_creators
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    # NOTE: Maybe have this part return T and F,
    # to handle stuff like the changelog not directly
    # starting out with a version entry
    def process_line(self, context_stack, line):
        top = context_stack[-1] 
        if (top != self):
            raise Exception("This is not the current context.")

        for create_context in self.context_creators:
            if create_context(context_stack, line):
                return True

        if not re.match(self.rest_re, line):
            context_stack.pop()
            return False

        self.root_str += line
        return True

    # TODO: For debugging, remove when done
    def __str__(self):
        return self.pretty_print(0)

    # Remove pretty print too!
    def pretty_print(self, indent = 0):
        indentation = '=' * indent

        return "\n".join([
#            indentation + "----START CONTEXT----",
             indentation + "ROOT: " + self.root_str,
#            indentation + "----CHILDREN----",
             '\n'.join([child.pretty_print(indent + 4) for child in self.children]),
#             '\n'.join([indentation + child.root_str for child in self.children]),
#            indentation + "----END CHILDREN----",
#            indentation + "----END CONTEXT----"
        ])

def context_starter(start_re):
    def context_starter_decorator(create_context):
        def start_context(context_stack, line):
            if not re.match(start_re, line):
                return False

            new_context = create_context(line)
            context_stack[-1].add_child(new_context)
            context_stack.append(new_context)
            return True

        return start_context

    return context_starter_decorator


# TODO: These are just test functions to test out the context.
# Remove these when the testing is finished.

def parse_file(log_path, global_context):
    with open('/Users/enis.inan/GitHub/puppet-agent-workflow/test-changelog/context/%s' % log_path, 'r') as f:
        context_stack = [global_context]

        for line in f:
            print("CONTEXT STACK\n: %s" % str(context_stack[-1]))
            print("")
            while(context_stack and not context_stack[-1].process_line(context_stack, line)):
                pass

            if not context_stack:
                break

        return global_context
