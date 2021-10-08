from unittest import TestCase

import static_data
import table_ops
import update_release
from table_ops import filter_table_by_keys
from update_release import update_release_table_with_changes


class TestUpdate(TestCase):
    def test_update_table(self, ):
        target = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/input_update_target.csv"
        result_file_name = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/result_output_from_input.csv"
        source = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/input_update_source.csv"
        header = ['Section', 'section_id', 'req_id', 'full_key', 'requirement', 'yes_2', 'other']
        header_data_to_copy = ['yes_2', 'other']
        updated_table, target_header = update_release_table_with_changes(target, source, result_file_name,
                                                                         header_data_to_copy)
        self.assertEqual(4, len(updated_table))

    def test_filter_table_dict_by_keys(self, ):
        keys = ['3.18/C-1-5', '7.1.4.2/C-1-9', '7.1.4.2/C-1-8', '3.18/C-1-3', '3.18/C-1-4', '9.10/C-0-3', '3.18/C-1-2',
                '3.18/C-1-1']
        table_input = static_data.RX_WORKING_OUTPUT_TABLE_TO_EDIT
        mapping_input = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/data_files/mapping_output_for_import.tsv"
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(mapping_input)
        new_table = filter_table_by_keys(table, key_fields, keys)
        table_ops.write_table("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output1/mapping_input_update_table.csv", new_table,
                              header)
        self.assertIs(len(keys), len(new_table))

    def test_filter_by_table_files(self, ):
        table_out= "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input1/to_do_undone_subset.csv"
        table_source= "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output1/to_do_undone.csv"
        table_target ="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/RX_WORKING_OUTPUT_TABLE_TO_EDIT.csv"
        update_release.make_new_table_with_row_keys_from_table(table_target,table_source,table_out)

    def test_filter_table_by_removing_keys(self, ):
        keys_to_filter_by = ['3.18/C-1-5', '7.1.4.2/C-1-9', '7.1.4.2/C-1-8', '3.18/C-1-3', '3.18/C-1-4', '9.10/C-0-3', '3.18/C-1-2',
                '3.18/C-1-1']
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(
            "/mapping_output_for_import.tsv")
        new_table = table_ops.filter_able_by_removing_keys(table, key_fields, keys_to_filter_by)

        table_ops.write_table(
            "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/test_update_table_mapped_removed.csv",
            new_table, header)
        table_f, key_fields_f, header_f, duplicate_rows_f = table_ops.read_table_sect_and_req_key(
            "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/test_update_table_mapped_removed.csv")

        #self.assertIs(len(table) - len(keys_to_filter_by), len(new_table))
        for key in keys_to_filter_by:
            self.assertIsNone(key_fields_f.get(key))
        for key in keys_to_filter_by:
            self.assertIsNotNone(key_fields.get(key))


    def test_read_table_sect_and_req_key(self):
        input_table = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/FILTERED_TABLE_TO_SEARCH.csv"
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(file_name=input_table,logging=True)

        self.assertIs(len(table) ,len(key_fields))

    def test_read_table_sect_and_req_key_no_req  (self):
        input_table = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input1/Working copy of CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - Undon.csv"
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(file_name=input_table,
                                                                                          logging=True)
        table_ops.write_table(
            "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output1/to_do_undone.csv",table, header)

    def test_write_file_fields_to_files(self):
        input_table = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/3_2.3.5-c-12-1_out.csv"
        table_ops.write_file_fields_to_files(input_table)


    def test_try_tabs(self):
        input_table = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/o_cdd-cts-tracker - 3_2.3.5_out.tsv"
        table, key_fields, header, duplicate_rows= table_ops.read_table_sect_and_req_key(input_table)
        print(str(table))

