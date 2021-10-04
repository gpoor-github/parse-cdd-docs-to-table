from unittest import TestCase

import static_data
import table_ops
from table_ops import filter_table_by_keys
from update_release import update_release_table_with_changes


class TestUpdate(TestCase):
    def test_update_table(self, ):
        target  = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/input_update_target.csv"
        result_file_name = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/result_output_from_input.csv"
        source = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/input_update_source.csv"
        header = ['Section', 'section_id', 'req_id', 'full_key', 'requirement', 'yes_2', 'other']
        header_data_to_copy =[ 'yes_2', 'other']
        updated_table, target_header = update_release_table_with_changes(target,source,result_file_name,header_data_to_copy)
        self.assertEqual(4,len(updated_table))


    def test_filter_table_dict_by_keys(self, ):
       keys = ['3.18/C-1-5', '7.1.4.2/C-1-9', '7.1.4.2/C-1-8', '3.18/C-1-3', '3.18/C-1-4', '9.10/C-0-3', '3.18/C-1-2','3.18/C-1-1']
       table, key_fields, header, duplicate_rows= table_ops.read_table_sect_and_req_key("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input1/mapping_output_for_import.csv")
       new_table = filter_table_by_keys(table, key_fields, keys)
       table_ops.write_table("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/test_update_table_mapped_only_mapped.csv",new_table,header)
       self.assertIs(len(keys),len(new_table))


    def test_filter_table_by_removing_keys(self, ):
       keys = ['3.18/C-1-5', '7.1.4.2/C-1-9', '7.1.4.2/C-1-8', '3.18/C-1-3', '3.18/C-1-4', '9.10/C-0-3', '3.18/C-1-2','3.18/C-1-1']
       table, key_fields, header, duplicate_rows= table_ops.read_table_sect_and_req_key("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input1/mapping_output_for_import.csv")
       new_table = table_ops.filter_able_by_removing_keys(table, key_fields, keys)
       table_ops.write_table("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/test_update_table_mapped_removed.csv",new_table,header)
       self.assertIs(len(table) - len(keys),len(new_table))
