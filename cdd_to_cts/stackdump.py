#  Block to comment
from __future__ import print_function
from itertools import chain
import traceback
import sys

def stackdump(id='', msg='HERE'):
    print('ENTERING STACK_DUMP' + (': '+id) if id else '')
    raw_tb = traceback.extract_stack()
    entries = traceback.format_list(raw_tb)

    # Remove the last two entries for the call to extract_stack() and to
    # the one before that, this function. Each entry consists of single
    # string with consisting of two lines, the script file path then the
    # line of source code making the call to this function.
    del entries[-2:]

    # Split the stack entries on line boundaries.
    lines = list(chain.from_iterable(line.splitlines() for line in entries))
    if msg:  # Append it to last line with name of caller function.
        lines[-1] += ' <-- ' + msg
        lines.append('LEAVING STACK_DUMP' + (': '+id) if id else '')
    print('\n'.join(lines))
    print()

if __name__ == '__main__':


    def func1():
        stackdump('A')

    def func2():
        func1()

    func1()
    print()
    func2()