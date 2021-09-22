import time

import static_data
import table_ops


def update_release_table_with_changes(original_sheet_file_name: str,
                                      updated_output_file_name: str = "output/updated_table.csv"):
    input_table, input_table_keys_to_index, input_header, duplicate_rows = table_ops.read_table(
        static_data.WORKING_ROOT+original_sheet_file_name)
    values_to_use_table, values_to_use_table_keys_to_index, values_to_use_input_header, values_to_use_duplicate_rows = table_ops.read_table(
        static_data.WORKING_ROOT+updated_output_file_name)

    updated_table, key_key1, key_key2 = table_ops.update_table(input_table,
                                                               input_table_keys_to_index,
                                                               input_header, values_to_use_table,
                                                               values_to_use_table_keys_to_index,
                                                               values_to_use_input_header,
                                                               static_data.merge_header)

    # table_ops.compare_tables(updated_table,input_table)
    table_ops.write_table(static_data.WORKING_ROOT+'output/release_updated_table3.csv', updated_table, input_header)

    print(
        f'keys missing 1  {key_key1} keys missing 2 {key_key2}\nkeys1 missing  {len(key_key1)} keys2 missing {len(key_key2)} of {len(updated_table)}')


def update_fullkey_table_with_only_new_changes(original_sheet_file_name: str, updated_output_file_name: str):
    full_before_gvp_sheet_table, full_before_gvp_sheet_table_keys_to_index, full_before_gvp_sheet_header, duplicate_rows1 = table_ops.read_table(
        original_sheet_file_name)

    values_to_use_table, values_to_use_table_keys_to_index, values_to_use_full_before_gvp_sheet_header, duplicate_rows2 = table_ops.read_table(
        "output/updated_table.csv")
    # merged_columns = static_data_holder.add_keys_only + static_data_holder.merge_header
    updated_table, key_key1, key_key2 = table_ops.update_table(full_before_gvp_sheet_table,
                                                               full_before_gvp_sheet_table_keys_to_index,
                                                               full_before_gvp_sheet_header, values_to_use_table,
                                                               values_to_use_table_keys_to_index,
                                                               values_to_use_full_before_gvp_sheet_header,
                                                               static_data.merge_header)

    table_ops.write_table(updated_output_file_name, updated_table, full_before_gvp_sheet_header)

    print(
        f'keys missing 1  {key_key1} keys missing 2 {key_key2}\nkeys1 missing  {len(key_key1)} keys2 missing {len(key_key2)} of {len(updated_table)}')
    table_ops.diff_tables(original_sheet_file_name, updated_output_file_name)


if __name__ == '__main__':
    start = time.perf_counter()
    # update_fullkey_table_with_only_new_changes()
    # original_sheet_file_name = "sachiyoAugust 23, 2_49 PM - CDD 11.csv"
    original_sheet_file_name = "data_files/version_up_there_sorted.csv"
    updated_output_file_name = 'output/updated_table.csv'
    update_release_table_with_changes(original_sheet_file_name, updated_output_file_name)
    table_ops.diff_tables(original_sheet_file_name, updated_output_file_name)

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
