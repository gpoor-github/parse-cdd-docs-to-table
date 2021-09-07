import csv

from comparesheets import read_table


def update_table(table1: [[str]], key_to_index1: dict, header1: [str], table2:[[str]], key_to_index2: dict, header2: [str],
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
        table_index1 = key_to_index1.get(key)
        table_index2 = key_to_index2.get(key)
        if table_index1 and table_index2:
            t1_row = table1[table_index1]
            t2_row = table2[table_index2]
            # Section,section_id,req_id
            for column in columns:
                if t2_row[header2.index(column)] and (len(t1_row[header1.index(column)]) <= 0):
                    t1_row[header1.index(column)] = t2_row[header2.index(column)]
        else:
            if table_index1:
                missingkeys2.add(key)
            else:
                missingkeys1.add(key)

    return table1, missingkeys1, missingkeys1


default_header: [] = (
    ['Section', 'section_id', 'req_id', 'Test Availability', 'Annotation?' ',''New Req for R?',
     'New CTS for R?', 'class_def', 'method', 'module',
     'Comment(internal) e.g. why a test is not possible ', 'Comment (external)',
     'New vs Updated(Q)', 'CTS Bug Id ', 'CDD Bug Id', 'CDD CL', 'Area', 'Shortened',
     'Test Level',
     '', 'external section_id', '', '', ''])
merge_header: [] = (
    ['Test Availability', 'class_def', 'method', 'module'])


def merge_tables(file1, file2):
    table1, key_fields1, header1 = read_table(file1)
    table2, key_fields2, header2 = read_table(file2)
    updated_table, missingkeys1, missingkeys1 = update_table(table1, key_fields1, header1, table2, key_fields2, header2,
                                                             merge_header)
    write_table("output/update_test.cvs", updated_table, default_header)
    return table1, key_fields1, header1, table2, key_fields2, header2


def write_table(file_name: str, table: [[str]], header: [str]):
    with open(file_name, 'w', newline='') as csv_output_file:
        table_writer = csv.writer(csv_output_file)
        table_writer.writerow(header)
        table_writer.writerows(table)
        csv_output_file.close()


if __name__ == '__main__':
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
