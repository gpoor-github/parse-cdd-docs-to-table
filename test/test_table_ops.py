from unittest import TestCase

import static_data
from update_release import update_release_table_with_changes


class TestUpdate(TestCase):
    def test_update_table(self, ):
        input_file_name = "input/output_from_input.csv"
        output_file_name = "output/output_from_input.csv"
        result_file_name = "output/result_output_from_input.csv"

        update_release_table_with_changes(input_file_name, output_file_name, result_file_name,
                                          static_data.update_manual_header)
