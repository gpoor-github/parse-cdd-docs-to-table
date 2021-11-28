#  Block to comment
import sys

import react
from table_ops import move_last_row_to_new_table

if __name__ == '__main__':
    keep_trying = True
    remove_line = True
    init_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/w.tsv"
    target_file =init_file
    while keep_trying:
        result = input("Select 'y' to start new file! ")
        if result.find("y") != -1:
            remove_line = True
        if remove_line:
            target_file = move_last_row_to_new_table(init_file)
        react.do_map_with_flat_file(target_file)
        result = input("Select 'y' to continue ")
        if result.find("y") == -1:
            keep_trying = False

    print(f" Completed processing {target_file}")
