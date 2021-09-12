import csv
import sys

import static_data_holder


def update_table(table1: [[str]], key_to_index1: dict, header1: [str], table2: [[str]], key_to_index2: dict,
                 header2: [str],
                 columns: [str]):
    """
This will take table1 and update missing values in the specified key_to_index1 at columns to the target table if empty.
    :param header2:
    :param columns:
    :param header1:
    :param key_to_index2:
    :param key_to_index1:
    :param table1:
    :param table2:
    :return:
    """
    missingkeys1: set = set()
    missingkeys2: set = set()

    for key in key_to_index1:
        if not key_to_index2.get(key) or not key_to_index1.get(key):
            continue
        table_index1 = int(key_to_index1.get(key))
        table_index2 = int(key_to_index2.get(key))
        if table_index1 and table_index2:
            t1_row = table1[table_index1]
            t2_row = table2[table_index2]
            # Section,section_id,req_id
            for column in columns:
                column1_idx = header1.index(column)
                column2_idx = header2.index(column)
                # if column1_idx in range(0,len(t1_row)) and column2_idx in range(0,len(column)) :
                #   if t2_row[column2_idx] and (len(t1_row[column1_idx]) <= 0):
                t1_row[column1_idx] = t2_row[column2_idx]

            if t1_row:
                table1[table_index1] = t1_row
        else:
            if table_index1:
                missingkeys2.add(key)
            else:
                missingkeys1.add(key)

    return table1, missingkeys1, missingkeys1


def merge_tables(file1, file2):
    table1, key_fields1, header1 = read_table(file1)
    table2, key_fields2, header2 = read_table(file2)
    updated_table, missingkeys1, missingkeys1 = update_table(table1, key_fields1, header1, table2, key_fields2, header2,
                                                             static_data_holder.merge_header)
    write_table("output/update_test.cvs", updated_table, static_data_holder.default_header)
    return table1, key_fields1, header1, table2, key_fields2, header2


def write_table(file_name: str, table: [[str]], header: [str]):
    with open(file_name, 'w', newline='') as csv_output_file:
        table_writer = csv.writer(csv_output_file)
        if header:
            table_writer.writerow(header)
        table_writer.writerows(table)
        csv_output_file.close()


def read_table(file_name: str) -> [[[str]], dict[str, int], [str]]:
    """],

    :rtype: {[[str]],dict,[]}
    """
    table = []
    header = []
    section_id_index = 1
    req_id_index = 2
    header_rows = 0
    key_fields: dict = dict()
    try:
        with open(file_name) as csv_file:

            csv_reader_instance = csv.reader(csv_file, delimiter=',')
            line_count = 0

            for row in csv_reader_instance:
                if line_count == 0:
                    try:
                        section_id_index = row.index("section_id")
                        req_id_index = row.index("req_id")
                        print(f'Found header for {file_name} names are {", ".join(row)}')
                        header = row
                        line_count += 1
                        header_rows = 1
                        table.append(row)
                        # Skip the rest of the loop... if there is an exception carry on and get the first row
                        continue
                    except ValueError:
                        message = f' Error: First row NOT header {row} default to section_id = col 1 and req_id col 2. First row of file {csv_file} should contain CSV with header like Section, section_id, etc looking for <Section> not found in {row}'
                        print(message)
                        raise SystemExit(message)
                        # Carry on and get the first row

                print(f'\t{row[0]} row 1 {row[1]}  row 2 {row[2]}.')
                table.append(row)
                table_index = line_count - header_rows
                # Section,section_id,req_id
                section_id_value = table[table_index][section_id_index].rstrip('.')
                req_id_value = table[table_index][req_id_index]
                if len(req_id_value) > 0:
                    key_value = '{}/{}'.format(section_id_value, req_id_value)
                elif len(section_id_value) > 0:
                    key_value = section_id_value
                key_fields[key_value] = table_index
                line_count += 1
                print(f'Processed {line_count} lines {key_value} ')
                print(f'For table {line_count}')
            print("End with file")
            return table, key_fields, header
    except IOError as e:
        print(f"Failed to open file {file_name} exception -= {type(e)} exiting...")
        sys.exit(f"Fatal Error Failed to open file {file_name}")

    # find urls that may help find the tests for the requirement


def diff_tables(file1, file2):
    table1, _key_fields1, header1 = read_table(file1)
    table2, _key_fields2, header2 = read_table(file2)
    key_set1 = set(_key_fields1.keys())
    key_set2 = set(_key_fields2.keys())
    intersection = key_set1.intersection(key_set2)
    dif_1_2 = key_set1.difference(key_set2)
    dif_2_1 = key_set2.difference(key_set1)
    print(f"\n\nIntersection={len(intersection)} 1=[{file1}] ^ 2=[{file2}] intersection = {intersection}")
    print(f"\nDifference 1st-2nd={len(dif_1_2)} [{file1}] - 2=[{file2}]  diff={dif_1_2}")
    print(f"\nDifference 2nd-1st={len(dif_2_1)} [{file2}] - 1=[{file1}] diff= {dif_2_1}")
    dif_1_2_dict:[str,set] = dict()
    dif_2_1_dict:[str,set]  = dict()
    for shared_key_to_table_index in intersection:
        i1 = _key_fields1.get(shared_key_to_table_index)
        i2 = _key_fields2.get(shared_key_to_table_index)
        dif_1_2_at_i1 = set(table1[i1]).difference(set(table2[i2]))
        if len(dif_1_2_at_i1) > 0 :  dif_1_2_dict[shared_key_to_table_index] = set(dif_1_2_at_i1)
        dif_2_1_at_i2 = set(table2[i2]).difference(set(table1[i1]))
        if len(dif_2_1_at_i2) > 0 :  dif_2_1_dict[shared_key_to_table_index] = set(dif_2_1_at_i2)
    print(f"\n\nf1=[{file1}] ^ f2=[{file2}] Difference 1st-2nd={len(dif_1_2)} 2st-1nd={len(dif_2_1)}")
    print(f"\nCompare shared rows 1st-2nd={len(dif_1_2_dict)} diff=[{dif_1_2_dict}]")
    print(f"\nCompare shared rows 2st-1nd={len(dif_2_1_dict)} diff= [{dif_2_1_dict}]")
    return dif_1_2, dif_2_1, intersection, dif_1_2_dict, dif_2_1_dict


def create_table_subset_for_release(_file1_for_subset, _file2_for_subset, output_file) -> ([[str]], [str]):

    _dif_1_2, _dif_2_1, intersection, dif_1_2_dict, dif_2_1_dict = diff_tables(_file1_for_subset,
                                                                               _file2_for_subset)
    table2_for_subset, key_fields2_for_subset, header2_for_subset = read_table(_file2_for_subset)
    table_out = list([[str]])
    for key in intersection:
        table_out.append(table2_for_subset[key_fields2_for_subset[key]])

    write_table(output_file, table_out, header2_for_subset)
    return table_out, header2_for_subset


def merge_table_example():

    _file1 = "input/new_recs_remaining_todo.csv"
    _file2 = "data_files/created_output.csv"
    _table1, _key_fields1, _header1, _table2, _key_fields2, _header2 = merge_tables(_file1 ,_file2)
    _key_set1 = set(_key_fields1.keys())
    _key_set2 = set(_key_fields2.keys())
    _dif_2_1 = _key_set2.difference(_key_set1)
    _dif_1_2 = _key_set1.difference(_key_set2)
    _inter_1_2 = _key_set1.intersection(_key_set2)

    print(f"\n\nIntersection={len(_inter_1_2)} 1=[{_file1}] ^ 2=[{_file2}] _intersection = {_inter_1_2}")
    print(f"\nDifference 1st-2nd={len(_dif_1_2)} [{_file1}] - 2=[{_file2}]  diff={_dif_1_2}")
    print(f"\nDifference 2nd-1st={len(_dif_2_1)} [{_file2}] - 1=[{_file1}] diff= {_dif_2_1}")


if __name__ == '__main__':
    _file1_before_g_eddy = "data_files/Eddie july 16 before graham CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - July 16, 10_57 AM - CDD 8.1.csv"
    _file1_sachiyo_recent = "data_files/after-sachiyo - August 23, 2_49 PM - CDD 11.csv"
    _file2_after_g = "data_files/gpoor-updated-sept-11-2021.csv"
    x_file1_for_subset = "./output/created_output.cvs"
    x_file2_for_subset = "./input/new_recs_full_todo.csv"
    x_dif_1_2, x_dif_2_1, x_intersection, x_dif_1_2_dict, x_dif_2_1_dict = diff_tables(_file1_sachiyo_recent, _file2_after_g,)
    merge_tables(_file1_sachiyo_recent,"output/subset_table")
