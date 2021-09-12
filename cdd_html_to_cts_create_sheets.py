import time

import data_sources
import static_data_holder
from table_ops import write_table, update_table

INPUT_TABLE_FILE_NAME = '2021-09-11-CDD-11-Sachiyo-Aug-4-restore.csv'


def create_populated_table(keys_to_find_and_write):
    table: [[str]] = []
    keys_to_table_index: dict[str, int] = dict()
    table_row_index = 0
    for temp_key in keys_to_find_and_write:
        key_str: str = temp_key
        key_str = key_str.rstrip(".").strip(' ')
        write_new_data_line_to_table(key_str, data_sources.key_to_full_requirement_text, table,
                                     table_row_index)  # test_file_to_dependencies)
        keys_to_table_index[key_str] = table_row_index
        table_row_index += 1
    return table, keys_to_table_index


def convert_version_to_number(section_id: str, requirement_id: str = '\0-00-00'):
    section_splits = section_id.split(".")
    section_as_number = ''
    for i in range(4):
        if i < len(section_splits):
            idx = 0
            for j in range(1, -1, -1):
                if j >= len(section_splits[i]):
                    section_as_number += '0'
                else:
                    section_as_number += section_splits[i][idx]
                    idx += 1
        else:
            section_as_number += "00"

    requirement_splits = requirement_id.split("-")
    requirement_as_number = f'{ord(requirement_splits[0][-1])}'
    for k in range(1, len(requirement_splits)):
        if len(requirement_splits[k]) > 1:
            requirement_as_number = f'{requirement_as_number}{requirement_splits[k]}'
        else:
            requirement_as_number = f'{requirement_as_number}0{requirement_splits[k]}'

    return f'"{section_as_number}.{requirement_as_number}"'


# Section,section_id,req_id,Test Availability,Annotation? ,New Req for R?,New CTS for R?,class_def,method,module,
# ['Section', 'section_id', 'req_id', 'Test Availability','class_def', 'method', 'module','full_key','requirement', 'key_as_number','search_terms','urls','file_name'])

def write_new_data_line_to_table(key_str: str, keys_to_sections: dict, table: [[str]], table_row_index: int):
    key_to_java_objects = data_sources.key_to_java_objects
    key_to_urls = data_sources.key_to_urls
    section_data = keys_to_sections.get(key_str)

    if len(table) <= table_row_index:
        table.append(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''])

    print(f"keys from  {table_row_index} [{key_str}]")
    key_str = key_str.rstrip(".").strip(' ')
    key_split = key_str.split('/')
    table[table_row_index][static_data_holder.new_header.index('section_id')] = key_split[0]

    table[table_row_index][static_data_holder.new_header.index('full_key')] = key_str
    if section_data:
        section_data_cleaned = '"{}"'.format(section_data.replace("\n", " "))
        table[table_row_index][static_data_holder.new_header.index('requirement')] = section_data_cleaned

    if len(key_split) > 1:
        table[table_row_index][static_data_holder.new_header.index('req_id')] = key_split[1]
        table[table_row_index][static_data_holder.new_header.index('key_as_number')] = convert_version_to_number(key_split[0], key_split[1])
        table[table_row_index][static_data_holder.new_header.index('urls')] = key_to_urls.get(key_str)
        table[table_row_index][static_data_holder.new_header.index('search_terms')] = key_to_java_objects.get(key_str)

        # This function takes a long time
        a_single_test_file_name, test_case_name, a_method, class_name, a_found_methods_string, matched = data_sources.handle_java_files_data(
            key_str)

        table[table_row_index][static_data_holder.new_header.index('module')] = test_case_name
        if a_single_test_file_name:
            table[table_row_index][static_data_holder.new_header.index('class_def')] = class_name
            table[table_row_index][static_data_holder.new_header.index('file_name')] = a_single_test_file_name
        if a_method:
            table[table_row_index][static_data_holder.new_header.index('method')] = a_method
            table[table_row_index][static_data_holder.new_header.index('Test Availability')] = "Test Available"

        if matched:
            table[table_row_index][static_data_holder.new_header.index('matched')] = matched
        if a_found_methods_string:
            table[table_row_index][static_data_holder.new_header.index('methods_string')] = a_found_methods_string

    else:
        table[table_row_index][static_data_holder.new_header.index('key_as_number')] = convert_version_to_number(key_split[0])
        print(f"Only a major key? {key_str}")


def cdd_html_to_cts_create_sheets(targets: str = 'all'):
    # if targets == 'new' or targets == 'all':
    # Write New Table
    table_for_sheet, keys_to_table_indexes = create_populated_table(data_sources.global_input_table_keys_to_index)
    write_table('output/created_output.csv', table_for_sheet, None)
    # else:
    #     table_for_sheet, keys_to_table_indexes = create_populated_table(input_table, keys_from_input_table, input_header )  # Just a smaller table
    if targets == 'append' or targets == 'all':
        # Write Augmented Table
        updated_table, key_key1, key_key2 = update_table(data_sources.global_input_table,
                                                         data_sources.global_input_table_keys_to_index,
                                                         data_sources.global_input_header, table_for_sheet,
                                                         keys_to_table_indexes, static_data_holder.new_header, static_data_holder.merge_header)
        write_table('output/updated_table.csv', updated_table, data_sources.global_input_header)

        print(
            f'keys missing 1  {key_key1} keys missing 2 {key_key2}\nkeys1 missing  {len(key_key1)} keys2 missing {len(key_key2)} of {len(updated_table)}')


if __name__ == '__main__':
    start = time.perf_counter()
    cdd_html_to_cts_create_sheets('all')
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')