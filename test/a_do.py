#  Block to comment
import shutil
import unittest
from os.path import exists

import react
import static_data
import table_ops
from helpers import read_file_to_string, write_file_to_string
from table_functions_for_release import update_release_table_with_changes
from table_ops import move_last_row_to_new_table, copy_matching_rows_to_new_table


class MyTestCase(unittest.TestCase):
    key_to_process ="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/keys_to_process.txt"
    # def xtest_last_in_table(self):
    #     init_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/w.tsv"
    #     target_file = move_last_row_to_new_table(init_file)
    #     react.do_map_with_flat_file(target_file)
    #     self.assertEqual(True, True)  # add assertion here
    #     print(target_file)
    #
    #
    # def xtest_requirement_hard_coded(self):
    #     dir = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/"
    #     init_file = dir + "w.tsv"
    #     req = "9.8/H-1-8"
    #     target_file = dir + "w_"+req.replace("/", "_") + ".tsv"
    #     target_file = copy_matching_rows_to_new_table(target_file, init_file, static_data.FULL_KEY, req)
    #     react.do_map_with_flat_file(target_file)
    #     self.assertEqual(True, True)  # add assertion here
    #     print(req)

    def test_requirement_prompt(self):
        dir = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/"

        source_file = dir + "w.tsv"
        file_exists = False
        key_file_exists = exists(self.key_to_process)
        req = ""
        if key_file_exists:
            req = read_file_to_string(self.key_to_process)
        if len(req) < 3:
            req = input("Enter Full key for file to work on:\n ")

        target_file = dir + "w_" + req.replace("/", "_") + ".tsv"

        try:
            file_exists = exists(target_file)
        except Exception as err:
            print("Exception " + err)
        if not file_exists:
            print(f"Creating new file {file_exists} pulled form {source_file}")
            target_file = copy_matching_rows_to_new_table(target_file, source_file, static_data.FULL_KEY, req)

        updated_table, target_header =react.do_map_with_flat_file(target_file)
        self.assertGreater(len(updated_table), 0,f"Table 0 sized= {target_file}")
        if len(updated_table) > 0:
            if not key_file_exists:
                write_file_to_string(self.key_to_process,req)
        print(req)



    def test_pull_results(self):
        dir = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/"
        key_file_exists = exists(self.key_to_process)
        req = ""
        if key_file_exists:
            req = read_file_to_string(self.key_to_process)
        if len(req) < 3:
            req = input("Enter key to pull final results from ")
        target_file = dir + "w_" + req.replace("/", "_") + ".tsv"
        flat_file = dir + "w_" + req.replace("/", "_") + "_flat.tsv"
        processed = target_file.replace('.tsv', "_processed.tsv")
        manual_result = target_file.replace('.tsv', "_manual_result.tsv")
        file_exists = False
        try :
            file_exists = exists(manual_result)
        except Exception as err:
            print("Exception "+err)
        if not file_exists:
            shutil.copy(target_file,manual_result)
        processed = table_ops.copy_matching_rows_to_new_table(processed, flat_file, static_data.TEST_AVAILABILITY)

        updated_table, target_header = update_release_table_with_changes(manual_result, processed, manual_result, static_data.cdd_to_cts_app_header)
        self.assertGreater(len(updated_table), 0,f"Table 0 sized= {manual_result}")  # add assertion here
        print(req)



if __name__ == '__main__':
    unittest.main()
