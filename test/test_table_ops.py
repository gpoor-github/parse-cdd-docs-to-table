from unittest import TestCase

import table_ops
import update_release
from table_ops import filter_first_table_by_keys_of_second
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

    def test_filter_cdd_12_table_dict_by_keys(self, ):

        keys = ['7/C-0-5', '9.9.3.1/C-1-7', '7/C-0-1', '7.3.3/A-3-2', '7.1.5/H-0-1', '5.1.5/C-2-1', '9.9.3.1/C-1-9',
                '9/C-0-2', '10.2/C-0-1',
                '5.4.5/C-1-2', '7.2/C-0-1', '9.7/C-1-1', '3.8.3.1/C-1-7', '11/C-3-1', '9.7/C-2-1', '9.5/W-1-1',
                '7.8.1/C-2-2', '6.1/C-0-1',
                '3.15/C-1-5', '10.1/C-0-2', '9.2/C-0-1', '9.9.3.1/C-1-8', '3.2.3.5/C-10-1', '8.5/C-3-1', '3/T-0-1',
                '9.9.3.2/C-1-5',
                '7.8.1/C-1-1', '9.5/H-3-1', '3.15/C-1-2', '11/C-2-1', '7.3.4/A-2-2', '7.8.2/C-1-2', '7.6.1/H-9-2',
                '7.4.2/C-1-6',
                '7.1.1.1/H-0-1', '7.5.3/C-1-3', '7.8.1/C-1-2', '5.4.5/C-1-3', '9.9.3.2/C-1-4', '3.9/C-1-1',
                '7.3.4/T-1-2', '9.5/W-2-1',
                '9.11.1/C-1-7', '8.3/C-2-1', '1.1.3/A-0-1', '7.8.1/C-1-3', '7/C-0-6', '7/C-0-4', '7.8.2/A-0-1',
                '3.1.1/C-0-1', '5.4.5/C-1-4',
                '5.3.1/T-0-6', '7.2.3/W-0-1', '6.1/H-0-1', '8.3/T-1-3', '9.9.3.1/C-1-12', '7.2.3/C-4-1',
                '3.15/C-1-4', '9.9.3.1/C-1-6', '9.9.3.1/C-1-10', '7.2.1/C-0-1', '3.2.3.5/C-12-2', '7.2.4/W-0-1',
                '7.3.4/W-2-1', '7.8.1/C-2-1', '5.3.7/C-2-1', '9.9.3.1/C-1-5', '5/C-0-3', '10.1/C-0-3', '9.9.3.2/C-1-2',
                '9.5/T-2-1', '7.6.1/T-0-1', '9.9.3.2/C-1-3', '7.8.2/C-1-3', '3.8.14/C-1-4', '9.5/H-2-1', '7.3.4/H-3-2',
                '7.8.2/C-2-2',
                '3.9/C-1-2', '9.9.3.2/C-1-1', '3.2.3.5/C-12-3', '7.8.2/C-1-1', '7/C-0-3', '7.7.2/C-1-1', '7/C-0-2',
                '7.6.1/W-0-2',
                '7.3.3/A-3-1', '4/C-0-4', '7.1.1.1/Tab-0-1', '3.15/C-1-3', '11/C-0-1', '7.8.2/C-2-1', '10.1/C-0-1',
                '9.2/C-0-2',
                '7.4.3/C-3-2', '7.3.4/Tab-1-1', '7.3.4/A-2-3', '5.6/C-2-1', '3.5/C-0-10', '7.1.4.5/C-2-1',
                '9.11.1/C-1-8', '3/A-0-2',
                '3.9.1.1/C-1-1', '9.9.3.1/C-1-14', '7.3.4/A-2-1', '3.7/C-0-1', '9.7/C-0-13', '7.6.2/C-0-3',
                '7.7.1/H-1-1', '11/C-0-2',
                '9.9.3.1/C-1-11', '9.9.3.2/C-1-6', '7.6.2/C-3-1', '7.6.2/C-0-1', '9.9.3.1/C-1-13', '10.2/C-0-2',
                '7.1.1.1/C-0-2',
                '5.4.5/C-1-1', '5.10/C-3-1', '7.6.1/H-10-1', '11/C-1-1', '11/C-0-3', '9.5/T-3-1', '7.3.4/H-3-1',
                '9.5/T-1-1']
        table_input = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/CDD-12-only-req.tsv"
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(table_input)
        new_table = filter_first_table_by_keys_of_second(table, key_fields, keys)
        table_ops.write_table(
            "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/cdd_12_diff_11.tsv",
            new_table,
            header)
        self.assertIs(len(keys), len(new_table))

    cdd_11_html_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_download.html"
    cdd_11_table_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_table_created.tsv"  # So no filter
    cdd_12_html_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_download.html"
    cdd_12_table_generated_from_html_all = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_full_table_from_html.tsv"
    cdd_12_table_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_table_all_1678.tsv"  # So no filter

    def test_make_table_keys_in_11_but_not_in_12(self, ):
        keys = ['4/C-0-1', '4/C-0-8', '9.5/C-1-1', '4/C-0-4', '9.9.3.1/C-1-9', '4/C-0-9', '3.15/C-1-4',
                '9.9.3.1/C-1-12', '9.9.3.1/C-1-6', '3.8.14/C-2-1', '7.3.4/A-2-2', '9.9.3.1/C-1-7', '3.15/C-1-5',
                '4/C-0-2', '9.9.3.1/C-1-8', '4/C-0-6', '9.9.3.1/C-1-10', '9.9.3.2/C-1-6', '9.9.3.2/C-1-3',
                '3.8.4/C-1-1', '3.15/C-1-2', '9.9.3.1/C-1-5', '9.9.3.2/C-1-4', '3.15/C-1-3', '9.9.3.1/C-1-14',
                '9.9.3.2/C-1-5', '4/C-0-7', '4/C-0-5', '9.9.3.1/C-1-13', '9.9.3.2/C-1-1', '4/C-0-3', '9.9.3.1/C-1-11',
                '9.9.3.2/C-1-2']
        cdd_11_table_generated_from_html_all = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_full_table_from_html.tsv"
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(
            cdd_11_table_generated_from_html_all)
        new_table = filter_first_table_by_keys_of_second(table, key_fields, keys)
        table_ops.write_table(
            "/a1_working/cdd_11_diff_12.tsv",
            new_table,
            header)
        self.assertIs(len(keys), len(new_table))

    def test_make_table_dict_by_keys(self, ):
        keys = ['9.8.2/T-5-2', '9.8.9/C-0-2', '2.2.7.1/H-1-5', '3.18/C-0-4', '9.10/C-1-11', '3.15/C-0-7',
                '7.1.4.1/A-0-3',
                '9.8.2/H-5-3', '3.18/C-0-1', '9.1/C-0-15', '9.9.3/C-1-12', '2.2.7.4/H-1-3', '3.9.3/A-1-1',
                '2.2.7.2/H-1-4',
                '9.8.2/H-4-2', '7.4.2.4/C-1-4', '7.1.4.1/A-0-1', '9.5/C-3-4', '3.5.2/C-1-3', '7.4.3/C-6-2',
                '7.3.10/C-1-9',
                '2.2.7.4/H-1-4', '3.5.2/C-1-6', '3.18/C-0-8', '9.8.6/C-0-7', '9.9.3/C-1-16', '2.2.7.4/H-2-2',
                '9.8.12/C-1-4',
                '3.18/C-0-2', '7.4.1/C-4-1', '7.4.2/C-1-10', '7.3.2/C-1-10', '7.4.2.4/C-1-3', '9.8.2/H-4-1',
                '7.3.8/C-1-3', '9.5/C-3-1', '7.1.4/C-1-11', '2.2.7.4/H-2-1', '7.4.2.4/C-1-6', '3.8.13/C-1-3',
                '7.4.2/C-1-8', '9.8.12/C-2-2', '2.2.7.1/H-1-2', '2.2.7.2/H-1-6', '3.5.1/C-1-9', '2.2.7.2/H-1-8',
                '7.3.10/C-3-6', '9.8.2/T-4-2', '2.2.7.3/H-1-1', '8.3/C-1-6', '9.9.3/C-1-6', '9.9.3/C-1-10',
                '9.1/C-0-12', '2.2.7.2/H-1-7', '9.1/C-0-14', '7.3.10/C-3-5', '7.1.4/C-2-3', '9.8.12/C-2-1',
                '2.2.7.2/H-1-2', '9.8.13/C-1-1', '9.9.3/C-1-15', '3.5.2/C-1-2', '9.1/C-4-3', '3.5.1/C-1-10',
                '9.8.12/C-1-3', '2.2.7.1/H-1-4', '9.11/C-1-6', '9.8.2/T-4-1', '3.2.3.5/C-16-1', '2.2.7.1/H-1-3',
                '7.1.4/C-2-5', '9.8.13/C-1-3', '2.2.7.2/H-1-1', '3.6/C-1-1', '9.5/C-2-2', '7.4.1/C-5-2', '7.4.2/C-1-7',
                '7.4.2.4/C-1-7', '2.2.7.2/H-1-3', '7.1.1.1/H-0-2', '3.18/C-0-3', '7.4.2.4/C-3-1', '3.5.2/C-1-4',
                '7.4.2/C-1-9', '9.9.3/C-1-7', '3.5.2/C-1-1', '3.18/C-0-5', '9.9.3/C-1-17', '3.18/C-0-7',
                '2.2.7.1/H-1-1', '2.2.7.4/H-1-1', '7.3.10/C-1-10', '9.8.12/C-1-2', '7.4.2.4/C-1-9', '9.9.3/C-1-9',
                '9.8.2/H-4-4', '7.3.10/C-0-2', '9.1/C-4-2', '9.5/C-3-3', '9.9.3/C-1-14', '7.1.4.1/A-0-2',
                '2.2.7.1/H-1-8', '9.1/C-1-1', '3.15/C-0-5', '9.8.10/C-1-5', '7.4.2.4/C-1-5', '7.4.1/C-5-1',
                '2.2.7.4/H-1-2', '9.5/C-3-2', '9.8.13/C-1-2', '9.8.2/H-4-3', '9.5/C-2-1', '7.4.3/C-6-1',
                '2.2.7.1/H-1-6', '7.3.10/C-2-9', '3.5.1/C-2-1', '7.1.4/C-2-4', '7.4.2.5/C-1-4', '3.9.1/C-1-9',
                '9/C-1-1', '3.15/C-0-6', '2.2.7.3/H-2-1', '7.3.8/C-1-4', '9.1/C-3-1', '3.9.1/C-1-8', '9.1/C-4-1',
                '2.2.7.2/H-1-5', '3.18/C-0-9', '9.8.2/H-5-1', '9.8.12/C-1-1', '9.8.2/H-5-2', '9.1/C-0-13',
                '9.9.3/C-1-5', '9.8.2/T-5-1', '3.18/C-0-6', '2.2.7.4/H-2-3', '2.2.7.4/H-2-4', '9.9.3/C-1-11',
                '2.2.7.1/H-1-7', '7.4.2.4/C-1-8', '9.9.3/C-1-8']
        cdd_12_table_generated_from_html_all = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_full_table_from_html.tsv"

        table_input = cdd_12_table_generated_from_html_all
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(table_input)
        new_table = filter_first_table_by_keys_of_second(table, key_fields, keys)
        new_header = ["Section", 'section_id', 'req_id', 'full_key', 'requirement', 'key_as_number', 'search_terms']
        table_ops.write_table(
            "/a1_working/cdd_12_diff_11.tsv",
            new_table,
            header)
        self.assertIs(len(keys), len(new_table))

    def test_filter_by_table_files(self, ):
        table_out = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/to_do_undone_subset.csv"
        table_source = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output1/to_do_undone.csv"
        table_target = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/RX_WORKING_OUTPUT_TABLE_TO_EDIT.csv"
        update_release.make_new_table_with_row_keys_from_table(table_target, table_source, table_out)

    def test_filter_table_by_removing_keys(self, ):
        keys_to_filter_by = ['3.18/C-1-5', '7.1.4.2/C-1-9', '7.1.4.2/C-1-8', '3.18/C-1-3', '3.18/C-1-4', '9.10/C-0-3',
                             '3.18/C-1-2',
                             '3.18/C-1-1']
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(
            "/mapping_output_for_import.tsv")
        new_table = table_ops.filter_able_by_removing_keys(table, key_fields, keys_to_filter_by)

        table_ops.write_table(
            "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/test_update_table_mapped_removed.csv",
            new_table, header)
        table_f, key_fields_f, header_f, duplicate_rows_f = table_ops.read_table_sect_and_req_key(
            "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/test_update_table_mapped_removed.csv")

        # self.assertIs(len(table) - len(keys_to_filter_by), len(new_table))
        for key in keys_to_filter_by:
            self.assertIsNone(key_fields_f.get(key))
        for key in keys_to_filter_by:
            self.assertIsNotNone(key_fields.get(key))

    def test_read_table_sect_and_req_key(self):
        input_table = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/FILTERED_TABLE_TO_SEARCH.csv"
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(file_name=input_table,
                                                                                          logging=True)

        self.assertIs(len(table), len(key_fields))

    def test_read_table_sect_and_req_key_no_req(self):
        input_table = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/Working copy of CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - Undon.csv"
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(file_name=input_table,
                                                                                          logging=True)
        table_ops.write_table(
            "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output1/to_do_undone.csv", table, header)

    def test_write_file_fields_to_files(self):
        input_table = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output1/3.2.3.5_output.tsv"
        table_ops.write_file_fields_to_files(input_table)

    def test_try_tabs(self):
        input_table = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/o_cdd-cts-tracker - 3_2.3.5_out.tsv"
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(input_table)
        print(str(table))
