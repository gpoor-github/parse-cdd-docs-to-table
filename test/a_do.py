#  Block to comment
import shutil
import unittest

import react
import static_data
import table_ops
from table_functions_for_release import update_release_table_with_changes
from table_ops import move_last_row_to_new_table, move_matching_rows_to_new_table


class MyTestCase(unittest.TestCase):
    def xtest_last_in_table(self):
        init_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/w.tsv"
        target_file = move_last_row_to_new_table(init_file)
        react.do_map_with_flat_file(target_file)
        self.assertEqual(True, True)  # add assertion here
        print(target_file)


    def xtest_requirement_hard_coded(self):
        dir = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/"
        init_file = dir + "w.tsv"
        req = "9.8/H-1-8"
        target_file = dir + "w_"+req.replace("/", "_") + ".tsv"
        target_file = move_matching_rows_to_new_table(target_file, init_file,static_data.FULL_KEY, req)
        react.do_map_with_flat_file(target_file)
        self.assertEqual(True, True)  # add assertion here
        print(req)

    def test_requirement_prompt(self):
        dir = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/"
        init_file = dir + "w.tsv"
        req = input("Enter Full Key ")
        target_file = dir + "w_" + req.replace("/", "_") + ".tsv"
        target_file = move_matching_rows_to_new_table(target_file, init_file, static_data.FULL_KEY, req)
        react.do_map_with_flat_file(target_file)
        self.assertEqual(True, True)  # add assertion here
        print(req)

        # add assertion here


    def test_pull_results(self):
        dir = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/"
        init_file = dir + "w.tsv"
        req = input("Enter Full Key ")
        target_file = dir + "w_" + req.replace("/", "_") + ".tsv"
        flat_file = dir + "w_" + req.replace("/", "_") + "_flat.tsv"
        result_file = target_file.replace('.tsv', "_result.tsv")
        final_result = target_file.replace('.tsv', "_final.tsv")
        shutil.copy(target_file,final_result)
        result_file = table_ops.move_matching_rows_to_new_table(result_file, flat_file, static_data.TEST_AVAILABILITY)
        update_release_table_with_changes(final_result, result_file, final_result, static_data.cdd_to_cts_app_header)
        print(req)

    def test_update_final(self):
        dir = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/"
        init_file = dir + "w.tsv"
        req = input("Enter Full Key ")
        target_file = dir + "w_" + req.replace("/", "_") + ".tsv"
        flat_file = dir + "w_" + req.replace("/", "_") + "_flat.tsv"
        result_file = target_file.replace('.tsv', "_result.tsv")
        final_result = target_file.replace('.tsv', "_final.tsv")
       # final_result = shutil.copy(target_file,final_result)
        update_release_table_with_changes(final_result, result_file, final_result, static_data.cdd_to_cts_app_header)
        print(req)


if __name__ == '__main__':
    unittest.main()
