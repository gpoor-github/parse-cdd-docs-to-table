#  Block to comment

#  Block to comment
import json
from unittest import TestCase

import check_sheet
import table_functions_for_release
from check_sheet import ReadSpreadSheet
from table_ops import add_table_new_rows, merge_tables_rows

cdd_11_gpoor = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/data_files/gpoor_final_completed_items_for_r.tsv"
cdd_11_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/cdd_11_DATA_SOURCES_CSV_FROM_HTML_1st.tsv"
md_11 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/md_android11-release.tsv"
md_11B = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/md_cdd-11.tsv"
md_12 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/md_cdd_12_master.tsv"
md_cdd_12_preview_mapping_gpoor_cherrypick_items_from_piper = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/md_cdd_12_preview_mapping_gpoor_cherrypick_items_from_piper.tsv"
cdd_11_downloaded_tsv = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/data_files/CDD_11_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - CDD 11_nov_2021_for_diff.tsv"
cdd_12_downloaded_tsv = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/X_a1_working/CDD-12 Nov-9-downloaded.tsv"
cdd_12_working = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/X_a1_working/CDD_12_CTS_downloaded_full_working_updated.tsv"
cdd_12_master_diff_md_11 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/X_a1_working/cdd_12_master_diff_md_11.tsv"
cdd_12_html="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/cdd_12_gen_html.tsv"
cdd_11_html="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/cdd_11_gen_html.tsv"

class TestCheckSheets(TestCase):
    def test_does_class_ref_file_exist(self):
        all_cdd_12 ="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/CDD_12_staging_downloaded-2021-12-6.tsv"
        december_6 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/find_annotations.tsv"
        annotations = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/data_files/annotations_mappings.tsv"
        sample_known_good = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/sample_sheet_for_mapping.tsv"
        rs = ReadSpreadSheet()
        result_dict, not_found, found = rs.does_class_ref_file_exist(annotations)
        print('results {}\n class file found={} found={} not found={}'.format(json.dumps(result_dict, indent=4),rs.found_class_count, rs.found_count, rs.not_found_count))

    def test_check_create_table_from_difference_and_source_html(self):

        table_functions_for_release.create_table_from_differences_and_source(cdd_11_html, cdd_12_html, cdd_12_html,
                                                                             "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/12_vs_11.tsv")

    def test_check_create_table_from_difference_and_source(self):

        table_functions_for_release.create_table_from_differences_and_source(md_11B, md_12, md_12, cdd_12_master_diff_md_11)

    def test_create_a_working_table_from_difference_and_source(self):
        created ="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/cdd_12_todo_created.tsv"
        done="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/done_of_155_manual.tsv"
        out="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/new_to_do_manual.tsv"
        table_functions_for_release.create_table_from_differences_and_source(done, created, created,
                                                                             out)


    def test_create_keyed_table_from_download(self):
        keys_downloaded="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/CDD_12_staging_downloaded_keys.tsv"
        merge1="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/CDD_12_staging_merge1.tsv"
        done_work = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/done_of_155_manual_c.tsv"
        source_downloaded = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/CDD_12_staging_downloaded-2021-12-6.tsv"

        table_functions_for_release.create_table_from_downloaded_sheet_add_full_keys(source_downloaded, keys_downloaded)
        merge_tables_rows(keys_downloaded,done_work,merge1)
        check_sheet.diff_tables_files(merge1,done_work)

    def test_merge_tables(self):
        done_work1 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/done_of_155_manual.tsv"
        done_work2 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/done_of_155_manual_c.tsv"
        done_work_merge = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/done_merge_of_manual.tsv"
        merge_tables_rows(done_work1,done_work2,done_work_merge)


