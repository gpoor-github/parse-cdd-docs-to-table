#  Block to comment

#  Block to comment

from unittest import TestCase


import update_release
from check_sheet import ReadSpreadSheet

cdd_11_gpoor = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/data_files/gpoor_final_completed_items_for_r.tsv"
cdd_11_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/cdd_11_DATA_SOURCES_CSV_FROM_HTML_1st.tsv"
md_11 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/md_android11-release.tsv"
md_11B = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/md_cdd-11.tsv"
md_12 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/md_cdd_12_master.tsv"
md_cdd_12_preview_mapping_gpoor_cherrypick_items_from_piper = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/md_cdd_12_preview_mapping_gpoor_cherrypick_items_from_piper.tsv"
cdd_11_downloaded_tsv = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/data_files/CDD_11_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - CDD 11_nov_2021_for_diff.tsv"
cdd_12_downloaded_tsv = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/CDD-12 Nov-9-downloaded.tsv"
cdd_12_working = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/CDD_12_CTS_downloaded_full_working_updated.tsv"
cdd_12_master_diff_md_11 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/cdd_12_master_diff_md_11.tsv"


class TestCheckSheets(TestCase):
    def test_does_class_ref_file_exist(self):
        annotation_12 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/mapping_output_for_import.tsv"

        rs = ReadSpreadSheet()
        result_dict, not_found, found = rs.does_class_ref_file_exist(annotation_12)

    def test_check_create_table_from_difference_and_source(self):

        update_release.create_table_from_differences_and_source(md_11B,md_12,md_12,cdd_12_master_diff_md_11)