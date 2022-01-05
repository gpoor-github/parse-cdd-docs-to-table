import parser_constants
import static_data
import table_ops
from table_ops import read_table_sect_and_req_key, filter_first_table_by_keys_of_second, write_table, remove_keys, \
    update_table


def update_table_column_subset(input_table_to_find_source_columns: str,
                               header_columns_to_copy: [],
                               output_file_to_write_updated_table: str) :
    source_table, source_table_keys_to_index, source_header, duplicate_rows = table_ops.read_table_sect_and_req_key(
        input_table_to_find_source_columns)

    column_subset_table, column_subset_key_to_index= table_ops.remove_table_columns(source_table,

                                                               source_header,
                                                               header_columns_to_copy)

    table_ops.write_table(output_file_to_write_updated_table,column_subset_table, header_columns_to_copy)

    return column_subset_table, column_subset_key_to_index


def merge_duplicate_row_for_column_set_for_flat_file(input_table_to_find_source_columns: str,
                                                     header_columns_as_key_set: [],
                                                     output_file_to_write_updated_table: str) :
    source_table, source_table_keys_to_index, source_header, duplicate_rows  = table_ops.read_table_sect_and_req_key(input_table_to_find_source_columns)
    target_table = merge_duplicate_row_for_column_set_for_flat(source_table, source_table_keys_to_index, source_header, header_columns_as_key_set)
    column_subset_table, column_subset_key_to_index=table_ops.remove_table_columns( target_table, source_header, static_data.flat_file_header )


    table_ops.write_table(output_file_to_write_updated_table,column_subset_table, static_data.flat_file_header )

def update_release_table_with_changes(table_to_update_and_write_to_output_file: str,
                                      values_to_use_for_update: str,
                                      output_file_to_write_updated_table: str,
                                      header_columns_to_copy: []):
    target_table, target_table_keys_to_index, target_header, duplicate_rows = table_ops.read_table_sect_and_req_key(
        table_to_update_and_write_to_output_file)
    values_to_use_table, values_to_use_table_keys_to_index, values_to_use_target_header, values_to_use_duplicate_rows = \
        table_ops.read_table_sect_and_req_key(values_to_use_for_update)

    updated_table, key_key1, key_key2 = table_ops.update_table(target_table,
                                                               target_table_keys_to_index,
                                                               target_header, values_to_use_table,
                                                               values_to_use_table_keys_to_index,
                                                               values_to_use_target_header,
                                                               header_columns_to_copy)

    # table_ops.compare_tables(updated_table,target_table)
    table_ops.write_table(output_file_to_write_updated_table, updated_table, target_header)

    # print(
    #     f'keys missing 1  {key_key1} keys missing 2 {key_key2}\nkeys1 missing  {len(key_key1)} keys2 missing {len(key_key2)} of {len(updated_table)}')
    # check_update(output_file_to_write_updated_table, table_to_update_and_write_to_output_file)
    return updated_table, target_header


def update_fullkey_table_with_only_new_changes(original_sheet_file_name: str, source_to_use_values: str,
                                               table_name_to_write: str):
    full_before_gvp_sheet_table, full_before_gvp_sheet_table_keys_to_index, full_before_gvp_sheet_header, duplicate_rows1 = table_ops.read_table_sect_and_req_key(
        original_sheet_file_name)

    values_to_use_table, values_to_use_table_keys_to_index, values_to_use_full_before_gvp_sheet_header, duplicate_rows2 = table_ops.read_table_sect_and_req_key(
        source_to_use_values)
    # merged_columns = static_data_holder.add_keys_only + static_data_holder.merge_header
    updated_table, key_key1, key_key2 = table_ops.update_table(full_before_gvp_sheet_table,
                                                               full_before_gvp_sheet_table_keys_to_index,
                                                               full_before_gvp_sheet_header, values_to_use_table,
                                                               values_to_use_table_keys_to_index,
                                                               values_to_use_full_before_gvp_sheet_header,
                                                               parser_constants.update_release_header)

    table_ops.write_table(table_name_to_write, updated_table, full_before_gvp_sheet_header)

    print(
        f'keys missing 1  {key_key1} keys missing 2 {key_key2}\nkeys1 missing  {len(key_key1)} keys2 missing {len(key_key2)} of {len(updated_table)}')
    check_update(original_sheet_file_name, table_name_to_write)


# This function is essential, called after SourceCrawlerReducer and before RxData main_do_create_table
def make_new_table_with_row_keys_from_table(original_sheet_file_name: str = static_data.DATA_SOURCES_CSV_FROM_HTML_1st,
                                            rows_to_use_table_file_name: str = static_data.FILTER_KEYS_DOWNLOADED_TABLE,
                                            table_name_to_write: str = static_data.FILTERED_TABLE_TO_SEARCH):
    to_update_table, to_update_table_keys_to_index, to_update_header, duplicate_rows1 = table_ops.read_table_sect_and_req_key(
        original_sheet_file_name)
    rows_to_use_table_not_needed, rows_to_use_table_keys_to_index, columns_to_use_not_needed, duplicate_rows2 = table_ops.read_table_sect_and_req_key(
        rows_to_use_table_file_name)
    updated_table = table_ops.filter_first_table_by_keys_of_second(to_update_table, to_update_table_keys_to_index,
                                                                   rows_to_use_table_keys_to_index.keys())
    table_ops.write_table(table_name_to_write, updated_table, to_update_header)
    check_update(original_sheet_file_name, table_name_to_write)


def check_update(original_sheet_file_name, table_name_to_write):
    from check_sheet import diff_tables_files
    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content = diff_tables_files(
        original_sheet_file_name, table_name_to_write)
    if len(dif_1_2) != 0 or len(dif_2_1) != 0:
        print(
            f"Warning: diff 1-2{len(dif_1_2)} 2-1{dif_2_1} Original table and updated table should have same number of row/keys")
    elif len(dif_1_2_dict_content) == 0 and len(dif_2_1_dict_content) == 0:
       print(f"Note: NO difference between {original_sheet_file_name} and {table_name_to_write} from update. Ignore if expected ")
    else:
        print(
            f"Table update seems to have updated correctly, no new or removed rows, content 1/2 {len(dif_1_2_dict_content)} updated \n details:{dif_1_2_dict_content}\n")
        print(
            f"Table update seems to have updated correctly, no new or removed rows, content 1/2 {len(dif_1_2_dict_content)} updated. Details of changes printed above")


def make_new_table_with_row_keys_from_table_example():
    row_keys_from_table = static_data.FILTER_KEYS_DOWNLOADED_TABLE
    new_table_to_made = static_data.FILTERED_TABLE_TO_SEARCH
    make_new_table_with_row_keys_from_table(static_data.DATA_SOURCES_CSV_FROM_HTML_1st, row_keys_from_table,
                                            new_table_to_made)

def update_release_table_with_changes_example():
    annotations ="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/data_files/annotations_mappings.tsv"
    annotation_header = ([parser_constants.TEST_AVAILABILITY, parser_constants.CLASS_DEF, parser_constants.METHOD,
                          parser_constants.MODULE, parser_constants.FILE_NAME, parser_constants.TEST_LEVEL,
                          parser_constants.ANNOTATION_])
    target_to_update = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/cdd_12_todo_remaining_manual.tsv"
    source_for_data="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/xCD12_3_9.9.3_in_progress/9.9.3.tsv"
    new_table_to_made = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/test.tsv"

    update_release_table_with_changes(target_to_update, source_for_data, new_table_to_made,
                                      annotation_header)

def create_table_from_differences_and_source(table_for_diff_1, table_for_diff_2, table_for_source, output_file_for_results):
    from check_sheet import diff_tables_files
    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content = diff_tables_files(table_for_diff_1,table_for_diff_2 )
    table_ops.make_new_table_from_keys(dif_2_1, table_for_source, output_file_for_results)

def create_table_from_downloaded_sheet_add_full_keys(table_file_for_source, output_file_for_results):
    table_for_source, source_keys, header_scr, duplicate_rows1 = table_ops.read_table_sect_and_req_key(table_file_for_source)
    table_target, key_to_index_target = table_ops.create_full_key_and_key_as_number( table_for_source,source_keys,header_scr, static_data.cdd_12_manual_merge_helper)
    table_ops.write_table(output_file_for_results, table_target, static_data.cdd_12_manual_merge_helper)

if __name__ == '__main__':
    cdd_11_downloaded_html = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/cdd_11_gen_html.tsv"
    cdd_12_downloaded_html = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/cdd_12_gen_html.tsv"
    sheet_released_cdd_12_on_2021_12_07_downloaded = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/data_files/download-2021-12-7-released-gvp-cts-tracker-CDD-12.tsv"

    cdd_12_html_vs_sheet_debt_diffs = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/cdd_12_html_vs_sheet_debt_diffs.tsv"

    cdd_12_html_vs_sheet_diffs = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/cdd_12_html_vs_sheet_diffs.tsv"
    cdd_11_vs_12_diffs = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/cdd_12_diff_html_11x.tsv"
    cdd_11_vs_12_diffs_diffed_with_done = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/cdd_11_vs_12_diffs_diffed_with_done.tsv"
    # merge_duplicate_row_for_column_set_for_flat_file("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/w_3.2.3.5_C-5-1_flat.tsv",
    #                                                  [static_data.CLASS_DEF,static_data.METHOD],
    #                                                  "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/w_3.2.3.5_C-5-1_flat_bla.tsv")
    # update_release_table_with_changes_example()
    create_table_from_differences_and_source(cdd_11_vs_12_diffs_diffed_with_done,cdd_12_html_vs_sheet_diffs,cdd_12_html_vs_sheet_diffs,cdd_12_html_vs_sheet_debt_diffs)


def merge_duplicate_row_for_column_set_for_flat(table_target: [[str]], key_to_index_target: dict, header_target: [str],
                                                columns: [str]):
    if len(table_target) == 0:
        return table_target, key_to_index_target
    test_target_index_str = parser_constants.table_delimiter.join(header_target)
    matched_term_index = header_target.index(static_data.MATCHED_TERMS)
    search_term_index = header_target.index(static_data.SEARCH_TERMS)

    unique_rows: dict = dict()
    for t_target_row in table_target:
        try:
            column_key = ""
            for column in columns:
                if test_target_index_str.find(column) > -1:
                    column_target_idx = header_target.index(column)
                    column_key = column_key + "_" + t_target_row[column_target_idx]
            previous_row = unique_rows.get(column_key)
            if previous_row:
                t_target_row[header_target.index(
                    static_data.MATCHED_TERMS)] = f"{previous_row[header_target.index(static_data.MATCHED_TERMS)]} {t_target_row[header_target.index(static_data.MATCHED_TERMS)]}"
            unique_rows[column_key] = t_target_row

        except Exception as err:
            print(
                f"Note:errors {str(err)} or index in update table, think it's okay, the tables for update should not match ")

    new_merged_table: [[str]] = list()
    for unique_row_key in unique_rows:
        row: [str] = unique_rows.get(unique_row_key)
        matched_terms: str = row[matched_term_index]
        if matched_terms.find(static_data.MATCHED_TERMS) == -1:  # Not header row
            search_terms: str = row[search_term_index]
            terms_set = set(search_terms.split(" "))
            matched_terms_set = set(matched_terms.split(" "))
            row[matched_term_index] = f"{len(terms_set.intersection(matched_terms_set))}: {matched_terms}"
            new_merged_table.append(row)

    return new_merged_table


def move_last_row_to_new_table(table_to_get_row: str) -> str:
    key_fields1_org: dict
    table1_org, key_fields1_org, header1_org, duplicate_rows1_org = read_table_sect_and_req_key(
        table_to_get_row)
    fields_to_write: list = list()
    key_to_row = ""
    for key in key_fields1_org:
        key_to_row = key
    new_table_file_name: str = f"{table_to_get_row.replace('.tsv', '')}_{key_to_row.replace('/', '_')}.tsv"
    result_file_name: str = f"{table_to_get_row.replace('.tsv', '')}_{key_to_row.replace('/', '_')}_manual_result.tsv"

    with open(result_file_name, 'w', newline=parser_constants.table_newline) as result_file:
        result_file.close()

    fields_to_write.append(key_to_row)
    new_table = filter_first_table_by_keys_of_second(table1_org, key_fields1_org, fields_to_write)
    write_table(new_table_file_name, new_table, header1_org)
    table1_org_minus_row = remove_keys(table1_org, key_fields1_org, fields_to_write)
    write_table(table_to_get_row, table1_org_minus_row, header1_org)
    return new_table_file_name


def update_manual_fields_from_files(input_file_to_be_updated_with_manual_terms: str,
                                    output_file_to_take_as_input_for_update: str,
                                    output_file: str = None):
    if None == output_file:
        output_file = input_file_to_be_updated_with_manual_terms
    table1_org, key_fields1_org, header1_org, duplicate_rows1_org = read_table_sect_and_req_key(
        input_file_to_be_updated_with_manual_terms, static_data.update_manual_header)
    update_header: [str] = [parser_constants.cdd_info_only_header]

    updated_table, update_header = update_manual_fields(table1_org, key_fields1_org, header1_org,
                                                        output_file_to_take_as_input_for_update, update_header)
    write_table(output_file, updated_table, update_header)


def update_manual_fields(input_table: [[str]], input_key_fields: dict, input_header: [str],
                         manual_data_source_file_name: str,
                         manual_data_source_header: [str] = None,
                         manual_fields_header: [str] = static_data.update_manual_header) -> ([[str]], [str]):
    table_source, key_fields_source, header_source, duplicate_rows_source = read_table_sect_and_req_key(
        manual_data_source_file_name, manual_data_source_header)
    updated_header = input_header

    updated_table, missingkeys1, missingkeys1 = update_table(input_table, input_key_fields, updated_header,
                                                             table_source, key_fields_source, header_source,
                                                             manual_fields_header)
    return updated_table, updated_header