import time

import data_sources
import static_data
from cdd_to_cts import table_ops, helpers
from cdd_to_cts.helpers import convert_version_to_number, convert_version_to_number_from_full_key
from cdd_to_cts.react import RxData
from table_ops import write_table, update_table


def create_populated_table(keys_to_find_and_write,header:[] = static_data.cdd_to_cts_app_header):
    table: [[str]] = []
    keys_to_table_index: dict[str, int] = dict()
    table_row_index = 0
    for temp_key in keys_to_find_and_write:
        key_str: str = temp_key
        key_str = key_str.rstrip(".").strip(' ')
        write_new_data_line_to_table(key_str, data_sources.key_to_full_requirement_text, table,
                                     table_row_index, header)  # test_file_to_dependencies)
        keys_to_table_index[key_str] = table_row_index
        table_row_index += 1
    return table, keys_to_table_index


# Section,section_id,req_id,Test Availability,Annotation? ,New Req for R?,New CTS for R?,class_def,method,module,
# ['Section', SECTION_ID, 'req_id', 'Test Availability','class_def', 'method', 'module','full_key','requirement', 'key_as_number','search_terms','urls','file_name'])

def write_new_data_line_to_table(key_str: str, keys_to_sections: dict, table: [[str]], table_row_index: int, header:[] = static_data.cdd_to_cts_app_header):
    key_to_java_objects = data_sources.key_to_java_objects
    key_to_urls = data_sources.key_to_urls
    section_data = keys_to_sections.get(key_str)
    row: [str] = list(header)
    for i in range(len(row)):
        row[i] = ''
    if len(table) <= table_row_index:
        table.append(row)

    print(f"keys from  {table_row_index} [{key_str}]")
    key_str = key_str.rstrip(".").strip(' ')
    key_split = key_str.split('/')
    table[table_row_index][header.index('Section')] = data_sources.section_to_data.get(
        key_split[0])

    table[table_row_index][header.index(static_data.SECTION_ID)] = key_split[0]

    table[table_row_index][header.index('full_key')] = key_str
    if section_data:
        section_data_cleaned = '"{}"'.format(section_data.replace("\n", " "))
        table[table_row_index][header.index(static_data.REQUIREMENT)] = section_data_cleaned

    if len(key_split) > 1:
        table[table_row_index][header.index(static_data.REQ_ID)] = key_split[1]
        table[table_row_index][header.index(static_data.KEY_AS_NUMBER)] = convert_version_to_number(
            key_split[0], key_split[1])
        table[table_row_index][header.index('urls')] = key_to_urls.get(key_str)
        table[table_row_index][header.index('search_terms')] = key_to_java_objects.get(key_str)

        # This function takes a long time
        a_single_test_file_name, test_case_name, a_method, class_name, a_found_methods_string, matched = data_sources.handle_java_files_data(
            key_str)

        table[table_row_index][header.index('module')] = test_case_name
        if a_single_test_file_name:
            table[table_row_index][header.index('class_def')] = class_name
            table[table_row_index][header.index(
                'file_name')] = static_data.CTS_SOURCE_PARENT + a_single_test_file_name
        if a_method:
            table[table_row_index][header.index('method')] = a_method
            table[table_row_index][header.index('Test Availability')] = "Test Available"

        if matched:
            table[table_row_index][header.index(static_data.MATCHED_FILES)] = matched
            table[table_row_index][header.index(static_data.MATCHED_TERMS)] = matched

        if a_found_methods_string:
            table[table_row_index][header.index('methods_string')] = a_found_methods_string

    else:
        # This function handles having just a section_id
        table[table_row_index][header.index(static_data.KEY_AS_NUMBER)] =convert_version_to_number_from_full_key(key_split[0])
        print(f"Only a major key? {key_str}")


def cdd_html_to_cts_create_sheets(targets: str = 'all',
                                  created_table_file=static_data.WORKING_ROOT + "output/created_table.csv",
                                  update_table_file=static_data.WORKING_ROOT + "output/updated_table.csv",
                                  header:[] = static_data.cdd_to_cts_app_header):
    # if targets == 'new' or targets == 'all':
    # Write New Table
    table_for_sheet, keys_to_table_indexes = create_populated_table(data_sources.global_input_table_keys_to_index)
    write_table(created_table_file, table_for_sheet, header)
    # else:
    #     table_for_sheet, keys_to_table_indexes = create_populated_table(input_table, keys_from_input_table, input_header )  # Just a smaller table
    if targets == 'append' or targets == 'all':
        # Write Augmented Table
        updated_table, key_key1, key_key2 = update_table(data_sources.global_input_table,
                                                         data_sources.global_input_table_keys_to_index,
                                                         data_sources.global_input_header, table_for_sheet,
                                                         keys_to_table_indexes, header,
                                                         static_data.merge_header)
        write_table(update_table_file, updated_table, data_sources.global_input_header)

        print(
            f'keys missing 1  {key_key1} keys missing 2 {key_key2}\nkeys1 missing  {len(key_key1)} keys2 missing {len(key_key2)} of {len(updated_table)}')


def create_full_table_from_cdd():
    table_for_sheet, keys_to_table_indexes = create_populated_table(data_sources.key_to_full_requirement_text)
    write_table('output/full_cdd.csv', table_for_sheet, static_data.cdd_info_only_header)


#
# if __name__ == '__main__':
#     start = time.perf_counter()
#     create_full_table_from_cdd()
#     cdd_html_to_cts_create_sheets('all')
#
#     end = time.perf_counter()
#     print(f'Took time {end - start:0.4f}sec ')

if __name__ == '__main__':
    start = time.perf_counter()
    rd = RxData()
    result_table = [[str]]
    rd.do_search().pipe(rd.get_pipe_create_results_table()).subscribe(
        on_next=lambda table: table_ops.write_table("output/built_table2.csv", table, static_data.cdd_to_cts_app_header),
        on_completed=lambda: print("completed"),
        on_error=lambda err: helpers.raise_error("in main", err))

    # rx.from_iterable(test_dic).subscribe( lambda value: print("Received {0".format(value)))
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
