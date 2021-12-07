#  Block to comment

#  Block to comment

from unittest import TestCase

import static_data
import table_functions_for_release


class TestUpdateRelease(TestCase):
    def test_update_table_column_subset(self):
        source_table_to_copy = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/X_a1_working/9.9.3.tsv"
        subset_table_to_create = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/X_a1_working/9.9.3_column_subset.tsv"
        fields_to_use = ["Section","section_id","req_id","requirement","Test Availability","class_def","method","module"]
        table_functions_for_release.update_table_column_subset(source_table_to_copy, fields_to_use, subset_table_to_create)
    def test_update_table_column_subset_cdd_12(self):
        source_table_to_copy = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/X_a1_working/9.9.3.tsv"
        subset_table_to_create = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/X_a1_working/9.9.3_column_subset.tsv"
        fields_to_use = ["Section","section_id","req_id","requirement","Test Availability","class_def","method","module"]
        table_functions_for_release.update_table_column_subset(source_table_to_copy, fields_to_use, subset_table_to_create)

    def test_merge_tables_remove_col_dec_8(self):
        source_table_to_copy = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/done_merge_of_manual_back.tsv"
        subset_table_to_create =  "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/done_merge_of_manual_col_removed_full.tsv"
        fields_to_use =static_data.cdd_12_full_header_for_ref
        table_functions_for_release.update_table_column_subset(source_table_to_copy, fields_to_use, subset_table_to_create)
