import csv

default_header: [] = (
    ['Section', 'section_id', 'req_id', 'Test', 'Availability', 'Annotation?' ',''New Req for R?',
     'New CTS for R?', 'class_def', 'method', 'module',
     'Comment(internal) e.g. why a test is not possible ', 'Comment (external)',
     'New vs Updated(Q)', 'CTS Bug Id ', 'CDD Bug Id', 'CDD CL', 'Area', 'Shortened',
     'Test Level',
     '', 'external section_id', '', '', ''])


def read_table(file_name: str):
    """

    :rtype: object
    """
    table = []
    header = []
    key_fields: dict = dict()
    with open(file_name) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            if line_count == 0:
                if row.index(default_header[0]) > -1:
                    print(f'Column names are {", ".join(row)}')
                    header = row
                    line_count += 1
                else:
                    raise Exception(
                        f' First row of file {csv_file} should contain CSV with header like {default_header} looking for <Section> not found in {row}')
            else:
                print(f'\t{row[0]} row 1 {row[1]}  row 2 {row[2]}.')
                table.append(row)
                table_index = line_count - 1
                # Section,section_id,req_id
                section_id_value = table[table_index][header.index("section_id")].rstrip('.')
                req_id_value = table[table_index][header.index("req_id")]
                if len(req_id_value) > 0:
                    key_value = '{}/{}'.format(section_id_value, req_id_value)
                elif len(section_id_value) > 0:
                    key_value = section_id_value
                key_fields[key_value] = table_index
                line_count += 1
                print(f'Processed {line_count} lines {key_value} ')
            print(f'For table {line_count}')
        print("End for loop")
        return table, key_fields, header

    # find urls that may help find the tests for the requirement


def compare_tables(file1, file2):
    table1, key_fields1, header1 = read_table(file1)
    table2, key_fields2, header2 = read_table(file2)
    return table1, key_fields1, header1, table2, key_fields2, header2




if __name__ == '__main__':
    _file1 = "data_files/cdd-10.csv"
    _file2 = "data_files/cdd-11-org.csv"
    _table1, _key_fields1, _header1, _table2, _key_fields2, _header2 = compare_tables(_file1, _file2)
    _key_set1 = set(_key_fields1.keys())
    _key_set2 = set(_key_fields2.keys())
    _dif_2_1 = _key_set2.difference(_key_set1)
    _dif_1_2 = _key_set1.difference(_key_set2)
    _inter_1_2 = _key_set1.intersection(_key_set2)

    print(f"\n\nIntersection={len(_inter_1_2)} 1=[{_file1}] ^ 2=[{_file2}] _intersection = {_inter_1_2}")
    print(f"\nDifference 1st-2nd={len(_dif_1_2)} [{_file1}] - 2=[{_file2}]  diff={_dif_1_2}")
    print(f"\nDifference 2nd-1st={len(_dif_2_1)} [{_file2}] - 1=[{_file1}] diff= {_dif_2_1}")
