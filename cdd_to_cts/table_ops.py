import csv
import sys

import parser_constants
import parser_helpers
from parser_constants import HEADER_KEY, SECTION_ID, REQ_ID, FULL_KEY


def remove_table_columns(table_source: [[str]], header_column_source: [str],
                         columns_to_use: [str]) \
        -> ([[str]], dict[str, int]):
    """ This will take table_source and make a new table only using the columns specified.
    :return  ([[str]], dict):
    """
    column_subset_table = list()
    column_subset_key_to_index = dict()
    test_source_index_str = parser_constants.table_delimiter.join(header_column_source) + ' '
    column_subset_table_idx_count = 0
    key = ""
    for source_row in table_source:
        try:
            column_subset_row = list()
            for column in columns_to_use:
                if not column or column=='':
                    continue
                if test_source_index_str.find(column + parser_constants.table_delimiter) > -1:  # Add space so names have less chance of overlap
                    header_column_source_idx = header_column_source.index(column)
                    source_value_to_use = source_row[header_column_source_idx]
                    column_subset_row.append(source_value_to_use)
            column_subset_table.append(column_subset_row)
            key = source_row[header_column_source.index(parser_constants.FULL_KEY)]
            column_subset_key_to_index[key] = column_subset_table_idx_count
            column_subset_table_idx_count += 1

        except Exception as err:
            parser_helpers.print_system_error_and_dump(
                f"Note: key {key} errors {str(err)} on removing columns... should not happen ")

    return column_subset_table, column_subset_key_to_index


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
    test_target_index_str = parser_constants.table_delimiter.join(header_target)
    test_source_index_str = parser_constants.table_delimiter.join(header_source)
    for key in key_to_index_target:
        try:
            table_index_source: int = key_to_index_source.get(key)
            table_index_target: int = key_to_index_target.get(key)
            if (table_index_source is not None) and (table_index_target is not None):
                t_target_row = table_target[table_index_target]
                t_source_row = table_source[table_index_source]
                # Section,section_id,req_id
                for column in columns:
                    if test_target_index_str.find(
                            parser_constants.table_delimiter + column + parser_constants.table_delimiter) > -1 and test_source_index_str.find(
                        parser_constants.table_delimiter + column + parser_constants.table_delimiter) > -1:
                        column_target_idx = header_target.index(column)
                        column_source_idx = header_source.index(column)
                        # if column_target_idx in range(0,len(t_target_row)) and column_source_idx in range(0,len(column)) :
                        #   if t_source_row[column_source_idx] and (len(t_target_row[column_target_idx]) <= 0):
                        t_target_row[column_target_idx] = t_source_row[column_source_idx]

                if None != t_target_row:
                    table_target[table_index_target] = t_target_row
                else:
                    if table_index_target:
                        missingkeys_source.add(key)
                    else:
                        missingkeys_target.add(key)
            else:
                print(
                    f"Note: key {key} it is probably okay, the tables for update should not match ")

        except Exception as err:
            print(
                f"Note: key {key} errors {str(err)} or index in update table, think it's okay, the tables for update should not match ")

    return table_target, missingkeys_target, missingkeys_source


def remove_keys(table_target: [[str]], key_to_index_target: dict, key_indexes_to_use: list):
    new_table: [[str]] = list()
    valid_keys_str = " ".join(key_indexes_to_use)
    for key in key_to_index_target:
        try:
            if valid_keys_str.find(key) == -1:
                table_index_target = int(key_to_index_target.get(key))
                t_target_row = table_target[table_index_target]
                new_table.append(t_target_row)

        except Exception as err:
            print(
                f"Error: key {key} errors {str(err)} or index in update table, think it's okay, the tables for update should not match ")

    return new_table


def copy_matching_rows_to_new_table(output_table_name: str, table_to_get_row: str, column_name: str,
                                    search_string: str = None) -> str:
    table_src, key_fields_src, header_src, duplicate_rows_src = read_table_sect_and_req_key(table_to_get_row)
    new_table: [[str]] = list()
    column_index = list(header_src).index(column_name)
    for row in table_src:
        value: str = row[column_index]
        if search_string is None:
            if value and value.find('') > -1:
                new_table.append(row)
        elif value.find(search_string) > -1:
            new_table.append(row)
    if not len(new_table) > 0:  # Header and one line at least
        print(
            f"copy_matching_rows_to_new_table No data found for [{search_string}] in col [{column_name}] in table [{table_to_get_row}] ")
        return None
    if len(new_table) == 1 and find_header(new_table):
        return None
    write_table(output_table_name, new_table, header_src)
    return output_table_name


def filter_first_table_by_keys_of_second(table_target: [[str]], key_to_index_target: dict,
                                         key_indexes_to_use: list) -> [[str]]:
    new_table: [[str]] = list()
    for key in key_indexes_to_use:
        try:
            value = key_to_index_target.get(key)
            if value is None:
                continue
            table_index_target = int(key_to_index_target.get(key))
            t_target_row = table_target[table_index_target]
            new_table.append(t_target_row)

        except Exception as err:
            print(
                f"Error: key {key} errors {str(err)} or index in update table, think it's okay, the tables for update should not match ")

    return new_table


def create_full_key_key_as_number2(key_indexes_to_use, table_for_source, header_src: [str], header_dst: [str],
                                   output_file_for_results):
    new_table: [[str]] = list()
    for key in key_indexes_to_use:
        try:
            table_index_target = int(key_indexes_to_use.get(key))
            source_row = table_for_source[table_index_target]
            full_key = f"{1}/{2}"
            target_row = []

        except Exception as err:
            print(
                f"Error: key {key} errors {str(err)} or index in update table, think it's okay, the tables for update should not match ")

    return new_table


def create_full_key_and_key_as_number(table_source: [[str]],
                                      key_to_index_source: dict[str,int],
                                      header_source: [str],
                                      header_target_column: [str])->([[str]],dict[str,int]):
    table_target: [[str]] = list()
    key_to_index_target: dict[str,int] =dict()
    section_index_src = parser_constants.DEFAULT_SECTION_ID_INDEX
    req_index_src = parser_constants.DEFAULT_REQ_ID_INDEX
    try:
        if not (header_source.index(SECTION_ID) > -1 or  header_source.index(REQ_ID) > -1):
            parser_helpers.raise_error_system_exit()
            return table_target, key_to_index_target
        else:
            section_index_src =header_source.index(SECTION_ID)
            req_index_src =header_source.index(REQ_ID)

        # potential_header_str.find(FULL_KEY) > -1:
        test_target_index_str = parser_constants.table_delimiter.join(header_target_column)
        test_source_index_str = parser_constants.table_delimiter.join(header_source)
        for key in key_to_index_source:
                table_index_source: int = key_to_index_source.get(key)
                if find_header(table_source) and table_index_source == 0:
                    continue
                source_row = table_source[table_index_source]
                table_index_target: int = 0
                new_target_row: [str] = [""] * len(header_target_column)
                # Section,section_id,req_id
                for column in header_target_column:

                    column :str = str(column)
                    if test_target_index_str.find(
                            parser_constants.table_delimiter + column + parser_constants.table_delimiter) > -1 and test_source_index_str.find(
                        parser_constants.table_delimiter + column + parser_constants.table_delimiter) > -1:
                        column_target_idx = header_target_column.index(column)
                        column_source_idx = header_source.index(column)
                        # if column_target_idx in range(0,len(t_target_row)) and column_source_idx in range(0,len(column)) :
                        #   if t_source_row[column_source_idx] and (len(t_target_row[column_target_idx]) <= 0):
                        new_target_row[column_target_idx] = source_row[column_source_idx]
                    else:
                        src_section_id = source_row[section_index_src]
                        src_req_id = source_row[req_index_src]
                        src_full_key =  f"{src_section_id}/{src_req_id}"
                        if column == parser_constants.FULL_KEY:
                            new_target_row[header_target_column.index(parser_constants.FULL_KEY)] =src_full_key
                        if column == parser_constants.KEY_AS_NUMBER:
                            new_target_row[header_target_column.index(
                                parser_constants.KEY_AS_NUMBER)] = parser_helpers.convert_version_to_number_from_full_key(src_full_key)
                full_key_target = new_target_row[header_target_column.index(parser_constants.FULL_KEY)]
                key_to_index_target[full_key_target]= len(table_target)
                table_target.append(new_target_row)

    except Exception as err:
       parser_helpers.raise_error_system_exit(f"Error in create_full_key_and_key_as_number {str(err)}", err)

    return table_target, key_to_index_target


def remove_none_requirements(table_target: [[str]], key_to_index_target: dict) -> [[str]]:
    new_table: [[str]] = list()
    new_key_indexes = dict()
    none_key_count = 0
    key_count = 0

    for key in key_to_index_target:

        try:
            if key.find("/") == -1:
                none_key_count += 1
                continue
            table_index_target = int(key_to_index_target.get(key))
            t_target_row = table_target[table_index_target]
            new_table.append(t_target_row)
            new_key_indexes[key] = key_count
            key_count += 1

        except Exception as err:
            print(
                f"Error: key {key} errors {str(err)} or index in update table, think it's okay, the tables for update should not match ")
    print(
        f"Found {none_key_count} non keys new table={len(new_table)}  original table {len(table_target)}")

    return new_table, new_key_indexes


def merge_tables(file1, file2, output_file):
    table1, key_fields1, header1, duplicate_rows1 = read_table_sect_and_req_key(file1)
    table2, key_fields2, header2, duplicate_rows2 = read_table_sect_and_req_key(file2)
    table_target, missing_keys_target, missing_keys_source = update_table(table1, key_fields1, header1, table2,
                                                                          key_fields2, header2,
                                                                          parser_constants.update_release_header)
    write_table(output_file, table_target, header1)
    return table_target, header1


def add_table_new_rows(table_target: list[[str]], key_to_table_target: dict[str, int], header_target: [str],
                       table_new_row_source: list[[str]], key_to_new_row_source: dict[str, int],
                       header_source: [str]) -> ([[str]], dict[str, int]):
    test_target_index_str = parser_constants.table_delimiter.join(header_target)
    test_source_index_str = parser_constants.table_delimiter.join(header_source)
    for key in key_to_new_row_source:
        try:
            target_row_index = key_to_table_target.get(key)
            if target_row_index is None:
                source_row_index = key_to_new_row_source.get(key)
                source_row = table_new_row_source[source_row_index]
                new_target_row = list()
                for column_target in header_target:
                    new_target_row.append("")
                for column in header_target:
                    column:str = str(column)
                    if not column or column == '':
                        continue
                    if test_target_index_str.find(column + parser_constants.table_delimiter) > -1 and test_source_index_str.find(column + parser_constants.table_delimiter) > -1:
                        column_target_idx = header_target.index(column)
                        column_source_idx = header_source.index(column)
                        # if column_target_idx in range(0,len(t_target_row)) and column_source_idx in range(0,len(column)) :
                        #   if t_source_row[column_source_idx] and (len(t_target_row[column_target_idx]) <= 0):
                        new_target_row[column_target_idx] = source_row[column_source_idx]
                    # end for
                key_to_table_target[key] = len(table_target)
                table_target.append(source_row)

        except Exception as err:
            parser_helpers.print_system_error_and_dump(
                f"Note: key {key} errors {str(err)} on add_table_new_rows().. should not happen ")

    return table_target, key_to_table_target


def merge_tables_rows(target_table:str, source_table:str, output_file:str):
    table_target, key_fields_target, header_target, duplicate_rows_target = read_table_sect_and_req_key(target_table)
    table_source, key_fields_source, header_source, duplicate_rows_source = read_table_sect_and_req_key(source_table)
    table_target, key_to_table_target = add_table_new_rows(table_target, key_fields_target, header_target, table_source,
                                                           key_fields_source, header_source)
    write_table(output_file, table_target, header_target)
    return table_target, header_target


def add_columns(manual_fields_header, updated_header):
    for column in manual_fields_header:
        try:
            updated_header.index(column)
        except ValueError:
            updated_header.append(column)


# Not in use, before conversion to tabs
# def write_file_fields_to_files(source_to_use_values: str,
#                                fields_to_write: [str] = static_data.cdd_to_cts_app_header) -> [[str]]:
#     table, keys_to_index, header, duplicate_rows = read_table_sect_and_req_key(source_to_use_values)
#     fields_to_write_str = " ".join(fields_to_write)
#     path_for_files_root = static_data.WORKING_ROOT + "/output/" + source_to_use_values.rstrip(".csv")
#
#     for i in range(0, len(table)):
#         row = table[i]
#         key: str = row[header.index(static_data.FULL_KEY)]
#         key_f = key.replace('/', '_')
#         req_path = f"{path_for_files_root}/{key_f}"
#         os.makedirs(req_path, exist_ok=True)
#         for j in range(0, len(row) - 1):
#             if j >= len(header):
#                 print("Error header and data out of sync")
#                 break
#             if fields_to_write_str.find(header[j]) > -1:
#                 value: str = row[j]
#                 if len(value) > 10:
#                     col = header[j]
#                     file_path = rf"{req_path}/{col}.txt"
#                     text_file = open(file_path, "w")
#                     if col != static_data.METHODS_STRING:
#                         value = value.replace(' ', '\n')
#                     value = value.replace(']', ']\n')
#                     text_file.write(value)
#                     text_file.close()


def write_table(file_name: str, table: [[str]], header: [str]) -> [[str]]:
    file_name = parser_helpers.find_valid_path(file_name)

    with open(file_name, 'w', newline=parser_constants.table_newline) as csv_output_file:
        table_writer = csv.writer(csv_output_file, quoting=csv.QUOTE_ALL, delimiter=parser_constants.table_delimiter)
        found_header = find_header(table)
        start_index = 0
        if found_header is not None and (len(found_header) > 0):
            table_writer.writerow(found_header)
            start_index = +1
        elif header is not None and (len(header) > 0):
            table_writer.writerow(header)
        else:
            parser_helpers.print_system_error_and_dump(f"Filename {file_name} has no header fatal")
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
        print(f"wrote table of size {len(table)}  to {file_name} with columns {str(header)}")

    return table


def find_key_indices(table: [[str]]) -> (int, int):
    section_id_index = parser_constants.DEFAULT_SECTION_ID_INDEX
    req_id_index = parser_constants.DEFAULT_REQ_ID_INDEX
    try:
        section_id_index = table[0].index(SECTION_ID)
        req_id_index = table[0].index(REQ_ID)
        print(f'write_table indexes names sect {section_id_index}/{req_id_index}')
    except  (AttributeError, ValueError, IndexError) as ie:
        print(f"error {str(ie)} handling finding header for table first row nothing to write", file=sys.stderr)
    return section_id_index, req_id_index


def find_full_key_index(table: [[str]]) -> int:
    full_key_index = parser_constants.DEFAULT_FULL_KEY_INDEX
    try:
        full_key_index = table[0].index(parser_constants.FULL_KEY)
        print(f' indexes names sect {full_key_index}')
    except  (AttributeError, ValueError, IndexError) as ie:
        print(f"error {str(ie)} handling finding header for table first row nothing to write", file=sys.stderr)
    return full_key_index


def find_header(table: [[str]]) -> [str]:
    header = None
    try:
        potential_header_str = " ".join(table[0])
        if potential_header_str.find(SECTION_ID) > -1 and \
                potential_header_str.find(REQ_ID) > -1 or \
                potential_header_str.find(FULL_KEY) > -1:
            header = table[0]
            print(f'write_table Found header, names are (truncated) {", ".join(table[0])[0:350]}')
        else:
            raise ValueError(f"Header not found (truncated){potential_header_str[0:250]}")
    except  (AttributeError, ValueError, IndexError) as ie:
        print(f'No row 0 in table just writing use the one passed im header {str(ie)} (truncated) {str(header)[0:250]}')
    return header


def convert_to_table_with_index_dict(table_keyed: dict[str, str], header: [str]) -> (
        [[str]], dict[str, int], [str]):
    index_table: [[str]] = list()
    table_index_dict: dict = dict()

    if table_keyed.get(HEADER_KEY):
        header = table_keyed.get(HEADER_KEY)

    table_index = 1
    for key in table_keyed:
        if key == HEADER_KEY:
            continue
        row = table_keyed.get(key)
        index_table.append(row)
        table_index_dict[key] = table_index
        table_index += 1
    return index_table, table_index_dict, header


def convert_to_keyed_table_dict(input_table: [[str]], input_header: [str]) -> (
        [[str]], dict[str, int], [str]):
    table_dict_req_ids_to_rows: dict = dict()
    found_header = find_header(input_table)  # So we know if we should advance a row or not.
    full_key_index = find_full_key_index(input_table)
    table_index = 0
    if found_header:
        table_dict_req_ids_to_rows[HEADER_KEY] = found_header
        table_index += 1
    elif input_header is not None and len(input_header) > 0:
        table_dict_req_ids_to_rows[HEADER_KEY] = input_header
        table_index += 1
    else:
        print("Waring No header convert_to_keyed_table_dict ", file=sys.stderr)

    for table_index in range(1, len(input_table)):
        row = input_table[table_index]
        key = row[full_key_index]
        table_dict_req_ids_to_rows[key] = row
    return table_dict_req_ids_to_rows, found_header


def read_table_key_at_index(file_name: str, key_index: int, has_header: bool = True, logging: bool = False) -> [[[str]],
                                                                                                                dict[
                                                                                                                    str, int],
                                                                                                                [str],
                                                                                                                dict[
                                                                                                                    str, str]]:
    file_name = parser_helpers.find_valid_path(file_name)
    table = []
    header = []
    key_fields: dict = dict()
    duplicate_rows: [str, str] = dict()

    try:
        with open(file_name, newline=parser_constants.table_newline, encoding=parser_constants.table_encoding) as csv_file:

            csv_reader_instance = csv.reader(csv_file, delimiter=parser_constants.table_delimiter,
                                             dialect=parser_constants.table_dialect)
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
                    parser_helpers.print_system_error_and_dump(
                        f"Index error {file_name} idx {table_index}  -= {type(e)} value {str(e)}...")
                except Exception as e1:
                    parser_helpers.print_system_error_and_dump(
                        f"General exception  {file_name} idx {table_index} -= {type(e1)} exiting..{str(e1)}")

                # end for rows

            if logging: print("End with file")
            if len(duplicate_rows) > 0:
                print(
                    f"Note, reading tables with duplicate 1 {file_name} has={len(duplicate_rows)} duplicates {duplicate_rows} ")
            else:
                duplicate_rows = None
            csv_file.close()
    except IOError as e:
        parser_helpers.print_system_error_and_dump(f"Failed to open file {file_name} exception -= {type(e)} exiting...")
    return table, key_fields, header, duplicate_rows


def read_table_sect_and_req_key(file_name: str, header_in: [str] = None, logging: bool = False) -> [[[str]],
                                                                                                    dict[str, int],
                                                                                                    [str],
                                                                                                    dict[str, str]]:
    """],

    :rtype: {[[str]],dict,[]}
    """
    file_name = parser_helpers.find_valid_path(file_name)

    table = []
    header = []
    section_id_index = 1
    req_id_index = 2
    key_fields: dict = dict()
    duplicate_rows: [str, str] = dict()

    try:
        with open(file_name, newline=parser_constants.table_newline, encoding=parser_constants.table_encoding) as csv_file:
            csv_reader_instance = csv.reader(csv_file, delimiter=parser_constants.table_delimiter,
                                             dialect=parser_constants.table_dialect)
            table_index = 0
            is_header_set = False

            if header_in is not None and len(header_in) > 0:
                is_header_set = True
                header = header_in

            for row in csv_reader_instance:
                try:
                    if not is_header_set:
                        for column in row:
                            try:
                                if parser_constants.cdd_info_only_header.index(column) > -1:
                                    header = row
                                    is_header_set = True
                                    if logging: print(f'Found header for {file_name} names are {", ".join(row)}')
                                    break
                                    # Skip the rest of the loop... if there is an exception carry on and get the first row
                                continue
                            except ValueError as ve:
                                message = f' Fatal,  exit Error: First row NOT header file={csv_file}   ToDo: Consider passing in header? row={row} default to section_id = col 1 and req_id col 2. First row of file should contain CSV with header like Section, section_id, etc looking for <Section> not found in {row}'
                                print(message)
                                parser_helpers.print_system_error_and_dump(message, ve)
                                # Carry on and get the first row
                    header_len = len(header)
                    if logging: print(f'\t{row[0]} row 1 {row[1]}  row 2 {row[2]}.')
                    # Section,section_id,req_id
                    for i in range(len(row), header_len):
                        row.append('*')
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
                    parser_helpers.print_system_error_and_dump(
                        f"Index ValueError row[{row}] at idx={table_index}  from {file_name}  -= {type(e)} value {str(e)}...")
            csv_file.close()
            # end for rows

            if logging: print("End with file")
            if len(duplicate_rows) > 0:
                print(
                    f"note, reading tables with duplicate 1 {file_name} has={len(duplicate_rows)} duplicates {duplicate_rows} ")
            else:
                duplicate_rows = None
            csv_file.close()
    except (IOError, IndexError) as e:
        parser_helpers.print_system_error_and_dump(f"Failed to open file {file_name} exception -= {type(e)} exiting...")
        raise SystemExit(f"Failed to open file {file_name} exception -= {type(e)} exiting...")
    except Exception as e2:
        parser_helpers.print_system_error_and_dump(
            f"Unexpected fatal exception[{str(e2)}] file {file_name}  in read_table_sect_and_req_key  exiting...")
        raise SystemExit(f"Failed to open file {file_name} exception -= {str(e2)} exiting...")

    return table, key_fields, header, duplicate_rows

    # find urls that may help find the tests for the requirement


def read_table_to_dictionary(file_name: str, logging: bool = False) -> (dict[str, str], [str]):
    table_dictionary = dict()
    table, key_fields, header, duplicate_rows = read_table_sect_and_req_key(file_name=file_name, logging=logging)
    for key in key_fields:
        table_dictionary[key] = table[key_fields[key]]

    return table_dictionary, header


def read_table_to_dictionary_key_index(file_name: str, key_index: int, logging: bool = False) -> (dict, []):
    table_dictionary = dict()
    table, key_fields, header, duplicate_rows = read_table_key_at_index(file_name, key_index, logging)
    for key in key_fields:
        table_dictionary[key] = table[key_fields[key]]

    return table_dictionary, header


def create_table_subset_for_release(_file1_for_subset, _file2_for_subset, output_file, columns_to_copy_header) -> (
        [[str]], [str]):
    from check_sheet import diff_tables_files

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


def make_new_table_from_keys(keys_to_use: iter, file_name_of_table_input: str, file_name_table_output: str):
    table, key_fields, header, duplicate_rows = read_table_sect_and_req_key(
        file_name_of_table_input)
    new_table = filter_first_table_by_keys_of_second(table, key_fields, keys_to_use)
    write_table(
        file_name_table_output,
        new_table,
        header)


def merge_table_example():
    _file_table_to_update = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/cdd_12_done_of_the_118_manual.tsv"
    _file_table_to_use_as_input = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_current_one/w_9_3.2.3.5_C-9-1_flat.tsv"
    _file_output = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working_12/cdd_12_done_of_the_118_manual.tsv"
    _table_merged, header_from_table_to_update = merge_tables_rows(_file_table_to_update, _file_table_to_use_as_input,
                                                                   _file_output)


if __name__ == '__main__':
    # _file1_before_g_eddy = "../data_files/Eddie july 16 before graham CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - July 16, 10_57 AM - CDD 8.1.tsv"
    # _file1_sachiyo_recent = "../data_files/after-sachiyo - August 23, 2_49 PM - CDD 11.tsv"
    # _file2_after_g = "../data_files/gpoor-updated-sept-11-2021.tsv"
    # before_graham = "../data_files/Eddie july 16 before graham CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - July 16, 10_57 AM - CDD 11.tsv"
    # latest_sheet = "../data_files/dups_removed.tsv"
    # latest2 = "../data_files/version_up_there_sorted.tsv"
    # x_file1_for_subset = "../output/created_output.cvs"
    # x_file2_for_subset = "../input/new_recs_full_todo.tsv"
    # release = "../output/release_updated_table2.tsv"
    # from_more_recent_cdd_html = "../data_files/cdd_full_from_more_recent_worse_version.tsv"
    # from_less_recent_cdd_html = "../data_files/cdd_full_from_less_recent_better_version.tsv"
    #
    # final_output = 'output/built_from_created2.tsv'
    # sheet_from_before_gpoor = "data_files/CDD-11-2021-07-14-before-gpoor.tsv"
    # sheet_from_server_no_mod = "data_files/CDD-11_2021-11-23-csv"
    # original_sheet_file_name1 = "data_files/CDD-11_2021-11-23.tsv"
    # # values_to_use_table_file1 = 'output/final_output_file.tsv'
    # sorted_sheet_does_it_matter = "data_files/CDD-11_2021-11-23-sorted.tsv"
    # new_updated_table_file1 = 'output/new_updated_table_for_release.tsv'
    # fresh = "data_files/CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - CDD 11 (5).tsv"
    merge_table_example()
