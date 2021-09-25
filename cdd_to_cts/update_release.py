import time

import static_data
import table_ops
from cdd_to_cts import helpers


def update_release_table_with_changes(target_sheet_file_name: str,
                                      values_to_use_table_file_local: str = "output/updated_table.csv",
                                      new_updated_table_file: str = 'output/new_updated_table_file.csv'):
    target_table, target_table_keys_to_index, target_header, duplicate_rows = table_ops.read_table(
        static_data.WORKING_ROOT + target_sheet_file_name)
    values_to_use_table, values_to_use_table_keys_to_index, values_to_use_target_header, values_to_use_duplicate_rows = table_ops.read_table(
        static_data.WORKING_ROOT + values_to_use_table_file_local)

    updated_table, key_key1, key_key2 = table_ops.update_table(target_table,
                                                               target_table_keys_to_index,
                                                               target_header, values_to_use_table,
                                                               values_to_use_table_keys_to_index,
                                                               values_to_use_target_header,
                                                               static_data.merge_header)

    # table_ops.compare_tables(updated_table,target_table)
    table_ops.write_table(static_data.WORKING_ROOT + new_updated_table_file, updated_table, target_header)

    print(
        f'keys missing 1  {key_key1} keys missing 2 {key_key2}\nkeys1 missing  {len(key_key1)} keys2 missing {len(key_key2)} of {len(updated_table)}')
    check_update(target_sheet_file_name, new_updated_table_file)


def update_fullkey_table_with_only_new_changes(original_sheet_file_name: str, source_to_use_values: str, table_name_to_write: str):
    full_before_gvp_sheet_table, full_before_gvp_sheet_table_keys_to_index, full_before_gvp_sheet_header, duplicate_rows1 = table_ops.read_table(
        original_sheet_file_name)

    values_to_use_table, values_to_use_table_keys_to_index, values_to_use_full_before_gvp_sheet_header, duplicate_rows2 = table_ops.read_table(
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


def check_update(original_sheet_file_name, table_name_to_write):
    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content = table_ops.diff_tables(
        original_sheet_file_name, table_name_to_write)
    if len(dif_1_2) != 0 or len(dif_2_1) != 0:
        helpers.raise_error(
            f"Error: diff 1-2{len(dif_1_2)} 2-1{dif_2_1} Original table and updated table should have same number of row/keys")
    elif len(dif_1_2_dict_content) == 0 or len(dif_2_1_dict_content) == 0:
        helpers.raise_error(f"Error: NO difference from update... you should figure out why Original ")
    else:
        print( f"Table update seems to have updated correctly, no new or removed rows, content 1/2 {len(dif_1_2_dict_content)} updated \n details:{dif_1_2_dict_content}\n")
        print( f"Table update seems to have updated correctly, no new or removed rows, content 1/2 {len(dif_1_2_dict_content)} updated. Details of changes printed above")


if __name__ == '__main__':
    start = time.perf_counter()
    # update_fullkey_table_with_only_new_changes()
    # original_sheet_file_name = "sachiyoAugust 23, 2_49 PM - CDD 11.csv"
    original_sheet_file_name1 = "data_files/version_up_there_sorted.csv"
    values_to_use_table_file = 'output/updated_table.csv'
    # values_to_use_table_file1 = 'output/rx_try14.csv'

    new_updated_table_file1 = 'output/new_updated_table_file2.csv'
    fresh = "data_files/CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - CDD 11 (5).csv"
    final_output_file = "output/built_from_created2.csv"

    update_release_table_with_changes(fresh, final_output_file, new_updated_table_file1)

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
