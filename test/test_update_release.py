#  Block to comment

#  Block to comment

from unittest import TestCase


import release_for_release


class TestUpdateRelease(TestCase):
    def test_update_table_column_subset(self):
        source_table_to_copy = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/9.9.3.tsv"
        subset_table_to_create = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/9.9.3_column_subset.tsv"
        fields_to_use = ["Section","section_id","req_id","requirement","Test Availability","class_def","method","module"]
        release_for_release.update_table_column_subset(source_table_to_copy, fields_to_use, subset_table_to_create)
