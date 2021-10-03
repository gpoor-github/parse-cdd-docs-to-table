from unittest import TestCase

import static_data
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
