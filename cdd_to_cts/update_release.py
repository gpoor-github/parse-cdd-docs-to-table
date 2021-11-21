import static_data
import table_ops

def update_table_column_subset(input_table_to_find_source_columns: str,
                               header_columns_to_copy: [],
                               output_file_to_write_updated_table: str) :
    source_table, source_table_keys_to_index, source_header, duplicate_rows = table_ops.read_table_sect_and_req_key(
        input_table_to_find_source_columns)

    column_subset_table, column_subset_key_to_index= table_ops.remove_table_columns(source_table,
                                                               source_table_keys_to_index,
                                                               source_header,
                                                               header_columns_to_copy)

    table_ops.write_table(output_file_to_write_updated_table,column_subset_table, header_columns_to_copy)

    return column_subset_table, column_subset_key_to_index

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

    print(
        f'keys missing 1  {key_key1} keys missing 2 {key_key2}\nkeys1 missing  {len(key_key1)} keys2 missing {len(key_key2)} of {len(updated_table)}')
    check_update(output_file_to_write_updated_table, table_to_update_and_write_to_output_file)
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
                                                               static_data.merge_header)

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
    target_to_update = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/cdd_12_todo_output.tsv"
    source_for_data="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/CDD_12_nov-9-updated_for-merge.tsv"
    new_table_to_made = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/diff_from_table.tsv"

    update_release_table_with_changes(target_to_update, source_for_data, new_table_to_made,
                                      [static_data.TEST_AVAILABILITY,static_data.CLASS_DEF,static_data.METHOD,static_data.MODULE])

def create_table_from_differences_and_source(table_for_diff_1, table_for_diff_2, table_for_source, output_file_for_results):
    from check_sheet import diff_tables_files
    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content = diff_tables_files(table_for_diff_1,table_for_diff_2 )
    table_ops.make_new_table_from_keys(dif_2_1, table_for_source, output_file_for_results)

if __name__ == '__main__':
    update_release_table_with_changes_example()
