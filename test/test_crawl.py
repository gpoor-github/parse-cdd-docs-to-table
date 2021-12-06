#  Block to comment

import unittest

from class_graph import make_bags_of_words_all, get_list_of_at_test_files


class MyTestCase(unittest.TestCase):
    def test_something(self):
        make_bags_of_words_all()
        self.assertEqual(True, False)  # add assertion here

    def test_get_list_of_at_test_files(self):
        test_files_list  = get_list_of_at_test_files()
        self.assertGreater(10000, len(test_files_list))  # add assertion here


if __name__ == '__main__':
    unittest.main()
