#  Block to comment
import shutil
import unittest
from os import remove
from os.path import exists

import helpers
import react
import static_data
import table_ops
from helpers import read_file_to_string, write_file_to_string
from table_functions_for_release import update_release_table_with_changes
from table_ops import copy_matching_rows_to_new_table


class MyTestCase(unittest.TestCase):
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

    def test_map_a_requirement(self):
        flat_file, req, target_file, source_file= build_file_names_from_key_file()

        file_exists = False
        if exists(flat_file):
            processed = table_ops.copy_matching_rows_to_new_table("test_processed_delete.tsv", flat_file, static_data.TEST_AVAILABILITY, None)
            if processed:
                table = table_ops.read_table_sect_and_req_key(processed)
                print(f"Done! {req} result is {table[1]}")
                return
        try:
            file_exists = exists(target_file)
            if file_exists:
                backup = target_file.replace('.tsv', "_backup.tsv")
                shutil.copy(src=target_file,dst=backup)
                flat_file_backup = flat_file.replace('.tsv', "_backup.tsv")
                shutil.copy(src=flat_file,dst=flat_file_backup)
        except Exception as err:
            print("Exception " + str(err))
        if not file_exists:
            print(f"Creating new file {file_exists} pulled form {source_file}")
            target_file = copy_matching_rows_to_new_table(target_file, source_file, static_data.FULL_KEY, req)

        flat_file, latest_result  = react.do_map_with_flat_file(target_file, flat_file, target_file)
        self.assertTrue(exists(latest_result), f" failed to create file = {latest_result}")
        if exists(latest_result):
            if not exists(source_file):
                write_file_to_string(source_file,req)
        print(f"end {req}")

    def test_do_all(self):
        if not update_manual_results_file():
            self.test_map_a_requirement()

    def test_update_manual_results_file(self):
        method_string = input("Enter key method_string ")

        self.assertTrue(update_manual_results_file(static_data.METHODS_STRING,method_string))



def update_manual_results_file(column:str=static_data.TEST_AVAILABILITY,search_str:str = None)-> bool:
    flat_file, req, target_file, source_file = build_file_names_from_key_file()
    processed = target_file.replace('.tsv', "_processed_temp.tsv")
    manual_result = target_file.replace('.tsv', "_manual_result.tsv")
    if not exists(flat_file):
        print(f"Source to update does not exist req = {req} file ={flat_file}")
        return False

    file_exists = False
    try :
         file_exists = exists(manual_result)
    except Exception as err:
        print("Exception "+str(err))
    if not file_exists:
        shutil.copy(target_file,manual_result)
    processed = table_ops.copy_matching_rows_to_new_table(processed, flat_file, column,search_str)
    if not processed:
        return False
    updated_table, target_header = update_release_table_with_changes(manual_result, processed, manual_result, static_data.cdd_to_cts_app_header)
    if len(updated_table) > 0:
        try:
            remove(processed)
            backup = target_file.replace('.tsv', "_backup.tsv")
            remove(path=backup)
            flat_file_backup = flat_file.replace('.tsv', "_backup.tsv")
            remove(path=flat_file_backup)
        except Exception as err:
            print("Exception "+str(err))
            print(req)
    return True

def build_file_names_from_key_file():
    key_to_process ="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/keys_to_process.txt"
    _dir = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/"
    source_file = _dir + "w.tsv"
    key_file_exists = exists(key_to_process)
    req = ""
    if key_file_exists:
        req = read_file_to_string(key_to_process)
    if len(req) < 3:
        req = input("Enter key to pull final results from ")
    target_file = _dir + "w_" + req.replace("/", "_") + ".tsv"
    flat_file = _dir + "w_" + req.replace("/", "_") + "_flat.tsv"
    return flat_file, req, target_file, source_file


if __name__ == '__main__':
    unittest.main()
