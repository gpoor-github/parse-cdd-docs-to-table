#  Block to comment

#  Block to comment
import json
from unittest import TestCase

import check_sheet
from check_sheet import ReadSpreadSheet
from table_ops import add_table_new_rows, merge_tables_rows

cdd_11_gpoor = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/data_files/gpoor_final_completed_items_for_r.tsv"
cdd_11_created = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/test/output/cdd_11_DATA_SOURCES_CSV_FROM_HTML_1st.tsv"
md_11 = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/output/md_android11-release.tsv"
md_11B = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/output/md_cdd-11.tsv"
md_12 = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/output/md_cdd_12_master.tsv"
md_cdd_12_preview_mapping_gpoor_cherrypick_items_from_piper = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/output/md_cdd_12_preview_mapping_gpoor_cherrypick_items_from_piper.tsv"
cdd_11_downloaded_tsv = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/data_files/CDD_11_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - CDD 11_nov_2021_for_diff.tsv"
cdd_12_downloaded_tsv = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/X_a1_working/CDD-12 Nov-9-downloaded.tsv"
cdd_12_working = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/X_a1_working/CDD_12_CTS_downloaded_full_working_updated.tsv"
cdd_12_master_diff_md_11 = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/X_a1_working/cdd_12_master_diff_md_11.tsv"
cdd_12_html="/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/output/cdd_12_gen_html.tsv"
cdd_11_html="/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/output/cdd_11_gen_html.tsv"

class TestCheckSheets(TestCase):
    def test_does_class_ref_file_exist(self):
        all_cdd_12 ="/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/a1_working_12/CDD_12_staging_downloaded-2021-12-6.tsv"
        december_6 = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/a1_working_12/find_annotations.tsv"
        annotations = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/data_files/annotations_mappings.tsv"
        sample_known_good = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/a1_working_12/sample_sheet_for_mapping.tsv"
        rs = ReadSpreadSheet()
        result_dict, not_found, found = rs.does_class_ref_file_exist(annotations)
        print('results {}\n class file found={} found={} not found={}'.format(json.dumps(result_dict, indent=4),rs.found_class_count, rs.found_count, rs.not_found_count))


    def test_merge_tables(self):
        done_work1 = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/a1_working_12/done_of_155_manual.tsv"
        done_work2 = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/a1_working_12/done_of_155_manual_c.tsv"
        done_work_merge = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/a1_working_12/done_merge_of_manual.tsv"
        merge_tables_rows(done_work1,done_work2,done_work_merge)


