import csv
import sys

from cdd_to_cts import static_data, helpers
from cdd_to_cts.static_data import SECTION_ID, REQ_ID, RX_WORKING_OUTPUT_TABLE_TO_EDIT, HEADER_KEY


def update_table(table_target: [[str]], key_to_index_target: dict, header_target: [str], table_source: [[str]],
                 key_to_index_source: dict,
                 header_source: [str],
                 columns: [str]):
    """
This will take table_target and update missing values in the specified key_to_index_target at columns to the target table if empty.
    :param header_source:
    :param columns:
    :param header_target:
    :param key_to_index_source:
    :param key_to_index_target:
    :param table_target:
    :param table_source:
    :return:
    """
    missingkeys_target: set = set()
    missingkeys_source: set = set()
    for key in key_to_index_target:
        try:
            if not key_to_index_source.get(key) or not key_to_index_target.get(key):
                continue
            table_index_target = int(key_to_index_target.get(key))
            table_index_source = int(key_to_index_source.get(key))
            test_target_index_str = ",".join(header_target)
            test_source_index_str = ",".join(header_source)
            if table_index_target and table_index_source:
                t_target_row = table_target[table_index_target]
                t_source_row = table_source[table_index_source]
                # Section,section_id,req_id
                for column in columns:
                    if test_target_index_str.find(column) > -1 and test_source_index_str.find(column) > -1:
                        column_target_idx = header_target.index(column)
                        column_source_idx = header_source.index(column)
                        # if column_target_idx in range(0,len(t_target_row)) and column_source_idx in range(0,len(column)) :
                        #   if t_source_row[column_source_idx] and (len(t_target_row[column_target_idx]) <= 0):
                        t_target_row[column_target_idx] = t_source_row[column_source_idx]

                if t_target_row:
                    table_target[table_index_target] = t_target_row
            else:
                if table_index_target:
                    missingkeys_source.add(key)
                else:
                    missingkeys_target.add(key)
        except Exception as err:
            print(
                f"Error: key {key} errors {str(err)} or index in update table, think it's okay, the tables for update should not match ")

    return table_target, missingkeys_target, missingkeys_source


def filter_first_table_by_keys_of_second(table_target: [[str]], key_to_index_target: dict, key_indexes_to_use: dict):
    new_table: [[str]] = list()
    for key in key_indexes_to_use:
        try:
            if not key_to_index_target.get(key):
                continue
            table_index_target = int(key_to_index_target.get(key))
            t_target_row = table_target[table_index_target]
            new_table.append(t_target_row)

        except Exception as err:
            print(
                f"Error: key {key} errors {str(err)} or index in update table, think it's okay, the tables for update should not match ")

    return new_table


def merge_tables(file1, file2):
    table1, key_fields1, header1, duplicate_rows1 = read_table_sect_and_req_key(file1)
    table2, key_fields2, header2, duplicate_rows2 = read_table_sect_and_req_key(file2)
    updated_table, missingkeys1, missingkeys1 = update_table(table1, key_fields1, header1, table2, key_fields2, header2,
                                                             static_data.merge_header)
    write_table("output/update_test.cvs", updated_table, static_data.current_cdd_11_header)
    return table1, key_fields1, header1, table2, key_fields2, header2


def update_manual_fields(input_table: [[str]], input_key_fields: dict, input_header: [str],
                         manual_data_source_file_name: str,
                         manual_data_source_header: [str] = None,
                         manual_fields_header: [str] = static_data.update_manual_header) -> ([[str]], [str]):
    table_source, key_fields_source, header_source, duplicate_rows_source = read_table_sect_and_req_key(
        manual_data_source_file_name, manual_data_source_header)
    updated_header = input_header
    for column in manual_fields_header:
        try:
            updated_header.index(column)
        except ValueError:
            updated_header.append(column)

    for row in input_table:
        for index in range(len(row), len(updated_header)):
            row.append(f"{index} of {updated_header[index] }")
    updated_table, missingkeys1, missingkeys1 = update_table(input_table, input_key_fields, updated_header,
                                                             table_source, key_fields_source, header_source,
                                                             manual_fields_header)
    return updated_table, updated_header


def write_table(file_name: str, table: [[str]], header: [str]) -> [[str]]:

    file_name = helpers.find_valid_path(file_name)

    with open(file_name, 'w', newline='') as csv_output_file:
        table_writer = csv.writer(csv_output_file)
        found_header = find_header(table,None)
        start_index = 0
        if found_header:
            table_writer.writerow(found_header)
            start_index=+1
        elif header:
            table_writer.writerow(header)
        else:
            helpers.raise_error(f"Filename {file_name} has no header fatal")
            raise SystemExit(f"Filename {file_name} has no header fatal")


        # get rid of bad rows
        for i in range(start_index, len(table)):
            row = table[i]
            # if  not row[len(row)-1].endswith('\n'):
            #     row[len(row) - 1] = row[len(row) - 1]  +'\n'
            if row and len(row) > 1:
                table_writer.writerow(row)
            else:
                print(f"Error writing bad table row [{row}]")
        csv_output_file.close()
    return table


def find_key_indices(table: [[str]]) -> (int, int):
    section_id_index = static_data.DEFAULT_SECTION_ID_INDEX
    req_id_index = static_data.DEFAULT_REQ_ID_INDEX
    try:
        section_id_index = table[0].index(SECTION_ID)
        req_id_index = table[0].index(REQ_ID)
        print(f'write_table indexes names sect {section_id_index}/{req_id_index}')
    except  (AttributeError, ValueError, IndexError) as ie:
        print(f"error handling finding header for table first row nothing to write", file=sys.stderr)
    return section_id_index, req_id_index


def find_full_key_index(table: [[str]]) -> int:
    full_key_index = static_data.DEFAULT_FULL_KEY_INDEX
    try:
        full_key_index = table[0].index(static_data.FULL_KEY)
        req_id_index = table[0].index(REQ_ID)
        print(f' indexes names sect {full_key_index}')
    except  (AttributeError, ValueError, IndexError) as ie:
        print(f"error handling finding header for table first row nothing to write", file=sys.stderr)
    return full_key_index


def find_header(table: [[str]],header:[str])->[str]:
    try:
        table[0].index(SECTION_ID)
        table[0].index(REQ_ID)
        header = table[0]
        print(f'write_table Found header, names are {", ".join(table[0])}')
    except  (AttributeError, ValueError, IndexError) as ie:
        print(f'No row 0 in table just writing use the one passed im header {str(ie)} {str(header)}')
    return header


def convert_to_table_with_index_dict(table_keyed: dict[str, str], header: [str], logging: bool = True) -> (
[[str]], dict[str, int], [str]):
    index_table: [[str]] = list()
    table_index_dict: dict = dict()

    if table_keyed.get(HEADER_KEY):
        header = table_keyed.get(HEADER_KEY)
    index_table.append(header)

    table_index = 1
    for key in table_keyed:
        if key == HEADER_KEY:
            continue
        row = table_keyed.get(key)
        index_table.append(row)
        table_index_dict[key] = table_index
        table_index += 1
    return index_table, table_index_dict, header


def convert_to_keyed_table_dict(input_table: [[str]], input_header: [str], logging: bool = True) -> (
[[str]], dict[str, int], [str]):
    table_dict_req_ids_to_rows: dict = dict()
    found_header = find_header(input_table, None)# So we know if we should advance a row or not.
    full_key_index = find_full_key_index(input_table)
    table_index = 0
    if found_header:
        table_dict_req_ids_to_rows[HEADER_KEY] = found_header
        table_index += 1
    elif input_header:
        table_dict_req_ids_to_rows[HEADER_KEY] = found_header
        table_index += 1
    else:
        print("Waring No header convert_to_keyed_table_dict ", file=sys.stderr)

    for table_index in range(1, len(input_table)):
        row = input_table[table_index]
        key = row[full_key_index]
        table_dict_req_ids_to_rows[key] = row
    return table_dict_req_ids_to_rows, found_header


def read_table_key_at_index(file_name: str, key_index: int, has_header: bool = True, logging: bool = True) -> [[[str]],
                                                                                                               dict[
                                                                                                                   str, int],
                                                                                                               [str],
                                                                                                               dict[
                                                                                                                   str, str]]:
    file_name = helpers.find_valid_path(file_name)
    table = []
    header = []
    key_fields: dict = dict()
    duplicate_rows: [str, str] = dict()

    try:
        with open(file_name) as csv_file:

            csv_reader_instance = csv.reader(csv_file, delimiter=',')
            table_index = 0

            for row in csv_reader_instance:
                try:
                    if has_header and table_index == 0:
                        if logging: print(f'Found header for {file_name} names are {", ".join(row)}')
                        header = row
                        table.append(row)
                        table_index += 1
                        continue
                    key_value = row[key_index].strip()
                    if logging: print(f'At idx {table_index} Key={key_value} row{table_index} {row} ')
                    table.append(row)
                    does_key_existing_index = key_fields.get(key_value)
                    if does_key_existing_index:
                        if logging: print(
                            f" Error duplicate key in table key [{key_value}] row = [{row}] index ={table_index} dup index ={does_key_existing_index}!")
                        duplicate_rows[key_value] = f"{row}||{table[does_key_existing_index]}"
                    key_fields[key_value] = table_index

                    table_index += 1
                except IndexError as e:
                    helpers.raise_error(f"Index error {file_name} idx {table_index}  -= {type(e)} value {str(e)}...")
                except Exception as e1:
                    helpers.raise_error(
                        f"General exception  {file_name} idx {table_index} -= {type(e1)} exiting..{str(e1)}")

                # end for rows

            if logging: print("End with file")
            if len(duplicate_rows) > 0:
                print(
                    f"ERROR, reading tables with duplicate 1 {file_name} has={len(duplicate_rows)} duplicates {duplicate_rows} ")
            else:
                duplicate_rows = None
            csv_file.close()
    except IOError as e:
        helpers.raise_error(f"Failed to open file {file_name} exception -= {type(e)} exiting...")
    return table, key_fields, header, duplicate_rows


def read_table_sect_and_req_key(file_name: str, logging: bool = False) -> [[[str]], dict[str, int], [str],
                                                                           dict[str, str]]:
    """],

    :rtype: {[[str]],dict,[]}
    """
    file_name = helpers.find_valid_path(file_name)

    table = []
    header = []
    section_id_index = 1
    req_id_index = 2
    key_fields: dict = dict()
    duplicate_rows: [str, str] = dict()

    try:
        with open(file_name) as csv_file:

            csv_reader_instance = csv.reader(csv_file, delimiter=',')
            table_index = 0
            is_header_set = False

            for row in csv_reader_instance:
                try:
                    if not is_header_set:
                        try:
                            section_id_index = row.index(SECTION_ID)
                            req_id_index = row.index(REQ_ID)
                            if logging: print(f'Found header for {file_name} names are {", ".join(row)}')
                            header = row
                            ##table.append(row)
                            is_header_set= True
                            # Skip the rest of the loop... if there is an exception carry on and get the first row
                            continue
                        except ValueError:
                            message = f' Error: First row NOT header {row} default to section_id = col 1 and req_id col 2. First row of file {csv_file} should contain CSV with header like Section, section_id, etc looking for <Section> not found in {row}'
                            print(message)
                            raise SystemExit(message)
                            # Carry on and get the first row

                    if logging: print(f'\t{row[0]} row 1 {row[1]}  row 2 {row[2]}.')
                    # Section,section_id,req_id
                    table.append(row)
                    table[table_index][section_id_index] = table[table_index][section_id_index].strip().rstrip('.')
                    section_id_value = table[table_index][section_id_index]
                    table[table_index][req_id_index] = table[table_index][req_id_index].strip()
                    req_id_value = table[table_index][req_id_index]
                    if len(req_id_value) > 0:
                        key_value = '{}/{}'.format(section_id_value.strip(), req_id_value.strip())
                    elif len(section_id_value) > 0:
                        key_value = section_id_value.strip()

                    does_key_existing_index = key_fields.get(key_value)
                    if does_key_existing_index:
                        if logging: print(
                            f" Error duplicate key in table key [{key_value}] row = [{row}] index ={table_index} dup index ={does_key_existing_index}!")
                        duplicate_rows[key_value] = f"{row}||{table[does_key_existing_index]}"
                    key_fields[key_value] = table_index

                    if logging: print(f'Processed {table_index} lines {key_value} ')
                    if logging: print(f'For table {table_index}')
                    table_index += 1
                except (IndexError, ValueError) as e:
                    helpers.raise_error(f"Index ValueError row[{row}] at idx={table_index}  from {file_name}  -= {type(e)} value {str(e)}...")

            # end for rows

            if logging: print("End with file")
            if len(duplicate_rows) > 0:
                print(
                    f"ERROR, reading tables with duplicate 1 {file_name} has={len(duplicate_rows)} duplicates {duplicate_rows} ")
            else:
                duplicate_rows = None
            csv_file.close()
    except (IOError, IndexError) as e:
        helpers.raise_error(f"Failed to open file {file_name} exception -= {type(e)} exiting...")
    return table, key_fields, header, duplicate_rows

    # find urls that may help find the tests for the requirement


def read_table_to_dictionary(file_name: str, logging: bool = False) -> (dict[str,str], [str]):
    table_dictionary = dict()
    table, key_fields, header, duplicate_rows = read_table_sect_and_req_key(file_name, logging)
    for key in key_fields:
        table_dictionary[key] = table[key_fields[key]]

    return table_dictionary, header


def read_table_to_dictionary_key_index(file_name: str, key_index: int, logging: bool = False) -> (dict, []):
    table_dictionary = dict()
    table, key_fields, header, duplicate_rows = read_table_key_at_index(file_name, key_index, logging)
    for key in key_fields:
        table_dictionary[key] = table[key_fields[key]]

    return table_dictionary, header


def diff_tables_files(file1, file2):
    table1, _key_fields1, header1, duplicate_rows1 = read_table_sect_and_req_key(file1)
    table2, _key_fields2, header2, duplicate_rows2 = read_table_sect_and_req_key(file2)
    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content = diff_tables(table1, _key_fields1,
                                                                                             table2, _key_fields2)

    report_diff(_key_fields1, _key_fields2, dif_1_2, dif_1_2_dict_content, dif_2_1, dif_2_1_dict_content,
                duplicate_rows1, duplicate_rows2, file1, file2, header1, header2, intersection)
    return dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content


def report_diff(_key_fields1, _key_fields2, dif_1_2, dif_1_2_dict_content, dif_2_1, dif_2_1_dict_content,
                duplicate_rows1, duplicate_rows2, file1, file2, header1, header2, intersection):
    print("\nDifferences in shared rows starts >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print(f"\n\nSee block below f1=[{file1}] ^ f2=[{file2}] Difference 1st-2nd={len(dif_1_2)} 2st-1nd={len(dif_2_1)}")
    print(f"\nCompare shared rows 1st-2nd={len(dif_1_2_dict_content)} diff=[{dif_1_2_dict_content}]")
    print(
        f"Differences 1st-2nd={len(dif_1_2_dict_content)} above  f1=[{file1}] ^ f2=[{file2}] . can be long <<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>\n")
    print(f"\nCompare shared rows 2st-1nd={len(dif_2_1_dict_content)} diff= [{dif_2_1_dict_content}]")
    print(f"See block above Difference  2st-1nd={len(dif_2_1)}  f2=[{file2}] 1st f1=[{file1}]")
    print("Differences in shared rows ends... can be long <<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>\n\n")
    print(f"\n\nIntersection={len(intersection)} =[{intersection}]")
    print(f"\nDifference 1st-2nd={len(dif_1_2)} [{file1}] - 2=[{file2}]  diff={dif_1_2}")
    print(f"\nDifference 2nd-1st={len(dif_2_1)} [{file2}] - 1=[{file1}] diff={dif_2_1}\n")
    header_set1 = set(header1)
    header_set2 = set(header2)
    if (len(header_set1.difference(header_set2)) + len(header_set2.difference(header_set1)) + len(dif_1_2) + len(
            dif_2_1)) == 0:
        print(f"No Different keys or headers f1=[{file1}]  f2=[{file2}]\n")
    else:
        print(
            f'Header dif1-2 [{header_set1.difference(header_set2)}] Header dif1-2 [{header_set2.difference(header_set1)}]'
            f'\nintersection=[{header_set1.intersection(header_set2)}]\n')
    handle_duplicates(duplicate_rows1, duplicate_rows2, file1, file2)
    print(f"\nSize of table_target={len(_key_fields1)} table_source={len(_key_fields2)} f1=[{file1}] ^ f2=[{file2}] ")
    print(
        f"Intersection of {len(intersection)}  content differs 1-2 {len(dif_1_2_dict_content)} and 2-1 {len(dif_2_1_dict_content)}  rows")
    print(f"Difference 1st-2nd={len(dif_1_2)} 2st-1nd={len(dif_2_1)}  ")


def diff_tables(table1, _key_fields1, table2, _key_fields2):
    file1 = "File1"
    file2 = "File2"

    key_set1 = set(_key_fields1.keys())
    key_set2 = set(_key_fields2.keys())
    intersection = key_set1.intersection(key_set2)
    dif_1_2 = key_set1.difference(key_set2)
    dif_2_1 = key_set2.difference(key_set1)
    dif_1_2_dict_content: [str, set] = dict()
    dif_2_1_dict_content: [str, set] = dict()

    for shared_key_to_table_index in intersection:
        i1 = _key_fields1.get(shared_key_to_table_index)
        i2 = _key_fields2.get(shared_key_to_table_index)
        dif_1_2_at_i1 = set(table1[i1]).difference(set(table2[i2]))
        if len(dif_1_2_at_i1) > 0:
            dif_1_2_dict_content[shared_key_to_table_index] = set(dif_1_2_at_i1)
        dif_2_1_at_i2 = set(table2[i2]).difference(set(table1[i1]))
        if len(dif_2_1_at_i2) > 0:
            dif_2_1_dict_content[shared_key_to_table_index] = set(dif_2_1_at_i2)

    return dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content


def handle_duplicates(duplicate_rows1, duplicate_rows2, file1, file2):
    if duplicate_rows1 and len(duplicate_rows1) > 0:
        print(f"Error duplicates! 1 {file1} has {len(duplicate_rows1)} {duplicate_rows1} ")
        for duplicate_key1 in duplicate_rows1:
            lines = duplicate_rows1.get(duplicate_key1).split('||')
            print("\n".join(lines))
        print(f"Error duplicates! 1 {file1} has {len(duplicate_rows1)} {duplicate_rows1} ")

        for duplicate_key1 in duplicate_rows1:
            lines = duplicate_rows1.get(duplicate_key1).split('||')
            i = 0
            for line in lines:
                if line:
                    i += 1
                    print(f"{str(line).strip('][')}")
    else:
        print(f"No duplicates for 1={file1}")
    if duplicate_rows2 and len(duplicate_rows2) > 0:
        for duplicate_key2 in duplicate_rows2:
            lines = duplicate_rows2.get(duplicate_key2).split('||')
            print(f"    key={duplicate_key2} ")
            i = 0
            for line in lines:
                if line:
                    i += 1
                    print(f"        {i})={line} ")
        print(f"Error duplicates! 2  {file2} has {len(duplicate_rows2)} {duplicate_rows2} ")
    else:
        print(f"No duplicates for  2={file2}")


def create_table_subset_for_release(_file1_for_subset, _file2_for_subset, output_file, columns_to_copy_header) -> (
[[str]], [str]):
    _dif_1_2, _dif_2_1, intersection, dif_1_2_dict, dif_2_1_dict = diff_tables_files(_file1_for_subset,
                                                                                     _file2_for_subset)
    table2_for_subset, key_fields2_for_subset, header2_for_subset, duplicate_rows2 = read_table_sect_and_req_key(
        _file2_for_subset)
    table_out = list([[str]])
    if len(columns_to_copy_header) == 0:
        for key in intersection:
            table_out.append(table2_for_subset[key_fields2_for_subset[key]])
    else:
        copy_columns = set(header2_for_subset).intersection(columns_to_copy_header)
        for key in intersection:
            row_source = table2_for_subset[key_fields2_for_subset[key]]
            row_target = list()
            for copy_column in copy_columns:
                row_index = list(header2_for_subset).index(copy_column)
                row_target.append(row_source[row_index])
            table_out.append(row_target)

    write_table(output_file, table_out, header2_for_subset)
    return table_out, header2_for_subset


def merge_table_example():
    _file1 = "input/new_recs_remaining_todo.csv"
    _file2 = "data_files/created_output.csv"
    _table1, _key_fields1, _header1, _table2, _key_fields2, _header2 = merge_tables(_file1, _file2)
    _key_set1 = set(_key_fields1.keys())
    _key_set2 = set(_key_fields2.keys())
    _dif_2_1 = _key_set2.difference(_key_set1)
    _dif_1_2 = _key_set1.difference(_key_set2)
    _inter_1_2 = _key_set1.intersection(_key_set2)

    print(f"\n\nIntersection={len(_inter_1_2)} 1=[{_file1}] ^ 2=[{_file2}] _intersection = {_inter_1_2}")
    print(f"\nDifference 1st-2nd={len(_dif_1_2)} [{_file1}] - 2=[{_file2}]  diff={_dif_1_2}")
    print(f"\nDifference 2nd-1st={len(_dif_2_1)} [{_file2}] - 1=[{_file1}] diff= {_dif_2_1}")


if __name__ == '__main__':
    _file1_before_g_eddy = "../data_files/Eddie july 16 before graham CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - July 16, 10_57 AM - CDD 8.1.csv"
    _file1_sachiyo_recent = "../data_files/after-sachiyo - August 23, 2_49 PM - CDD 11.csv"
    _file2_after_g = "../data_files/gpoor-updated-sept-11-2021.csv"
    before_graham = "../data_files/Eddie july 16 before graham CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - July 16, 10_57 AM - CDD 11.csv"
    latest_sheet = "../data_files/dups_removed.csv"
    latest2 = "../data_files/version_up_there_sorted.csv"
    x_file1_for_subset = "../output/created_output.cvs"
    x_file2_for_subset = "../input/new_recs_full_todo.csv"
    release = "../output/release_updated_table2.csv"
    from_more_recent_cdd_html = "../data_files/cdd_full_from_more_recent_worse_version.csv"
    from_less_recent_cdd_html = "../data_files/cdd_full_from_less_recent_better_version.csv"

    final_output = 'output/built_from_created2.csv'
    sheet_from_before_gpoor = "data_files/CDD-11-2021-07-14-before-gpoor.csv"
    sheet_from_server_no_mod = "data_files/CDD-11_2021-11-23-csv"
    original_sheet_file_name1 = "data_files/CDD-11_2021-11-23.csv"
    # values_to_use_table_file1 = 'output/final_output_file.csv'
    sorted_sheet_does_it_matter = "data_files/CDD-11_2021-11-23-sorted.csv"
    new_updated_table_file1 = 'output/new_updated_table_for_release.csv'
    # update_manual_fields(static_data.RX_WORKING_OUTPUT_TABLE_TO_EDIT, static_data.FILTERED_TABLE_TO_SEARCH)

    fresh = "data_files/CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - CDD 11 (5).csv"
    x_dif_1_2, x_dif_2_1, x_intersection, x_dif_1_2_dict, x_dif_2_1_dict = diff_tables_files(
        _file1_sachiyo_recent,
        "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/full_cdd.csv")
# merge_tables(_file1_sachiyo_recent,"output/subset_table")
