#  Block to comment

#  Block to comment
import json
from unittest import TestCase
import input_data_from_cts
from cdd_to_cts import table_ops
from cdd_to_cts.inject_annotations_into_cts import ReadSpreadSheet

cdd_11_gpoor = "parse-cdd-docs-to-tabledata_files/gpoor_final_completed_items_for_r.tsv"
cdd_11_created = "parse-cdd-docs-to-tabletest/output/cdd_11_DATA_SOURCES_CSV_FROM_HTML_1st.tsv"
md_11 = "parse-cdd-docs-to-tableoutput/md_android11-release.tsv"
md_11B = "parse-cdd-docs-to-tableoutput/md_cdd-11.tsv"
md_12 = "parse-cdd-docs-to-tableoutput/md_cdd_12_master.tsv"
md_cdd_12_preview_mapping_gpoor_cherrypick_items_from_piper = "parse-cdd-docs-to-tableoutput/md_cdd_12_preview_mapping_gpoor_cherrypick_items_from_piper.tsv"
cdd_11_downloaded_tsv = "parse-cdd-docs-to-tabledata_files/CDD_11_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - CDD 11_nov_2021_for_diff.tsv"
cdd_12_downloaded_tsv = "parse-cdd-docs-to-tableX_a1_working/CDD-12 Nov-9-downloaded.tsv"
cdd_12_working = "parse-cdd-docs-to-tableX_a1_working/CDD_12_CTS_downloaded_full_working_updated.tsv"
cdd_12_master_diff_md_11 = "parse-cdd-docs-to-tableX_a1_working/cdd_12_master_diff_md_11.tsv"
cdd_12_html="parse-cdd-docs-to-tableoutput/cdd_12_gen_html.tsv"
cdd_11_html="parse-cdd-docs-to-tableoutput/cdd_11_gen_html.tsv"

class TestCheckSheets(TestCase):
    def test_does_class_ref_file_exist(self):
        all_cdd_12 ="parse-cdd-docs-to-tablea1_working_12/CDD_12_staging_downloaded-2021-12-6.tsv"
        december_6 = "parse-cdd-docs-to-tablea1_working_12/find_annotations.tsv"
        annotations = "parse-cdd-docs-to-tabledata_files/annotations_mappings.tsv"
        sample_known_good = "parse-cdd-docs-to-tablea1_working_12/sample_sheet_for_mapping.tsv"
        rs = ReadSpreadSheet()
        result_dict, not_found, found = rs.does_class_ref_file_exist(annotations)
        print('results {}\n class file found={} found={} not found={}'.format(json.dumps(result_dict, indent=4), rs.found_class_count, rs.found_method_count, rs.not_found_count))


    def test_merge_tables(self):
        done_work1 = "parse-cdd-docs-to-tablea1_working_12/done_of_155_manual.tsv"
        done_work2 = "parse-cdd-docs-to-tablea1_working_12/done_of_155_manual_c.tsv"
        done_work_merge = "parse-cdd-docs-to-tablea1_working_12/done_merge_of_manual.tsv"
        table_ops.merge_tables_rows(done_work1,done_work2,done_work_merge)


