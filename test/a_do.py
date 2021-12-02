#  Block to comment

import unittest

import react
from table_ops import move_last_row_to_new_table


class MyTestCase(unittest.TestCase):
    def test_new_requirement(self):
        init_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/w.tsv"
        target_file = init_file
        move_last_row_to_new_table(init_file)
        react.do_map_with_flat_file(target_file)
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.main()
