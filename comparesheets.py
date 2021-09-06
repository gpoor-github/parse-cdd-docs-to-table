import csv

default_header: [] = (
    ['Section', 'section_id', 'req_id', 'Test', 'Availability', 'Annotation?' ',''New Req for R?',
     'New CTS for R?', 'class_def', 'method', 'module',
     'Comment(internal) e.g. why a test is not possible ', 'Comment (external)',
     'New vs Updated(Q)', 'CTS Bug Id ', 'CDD Bug Id', 'CDD CL', 'Area', 'Shortened',
     'Test Level',
     '', 'external section_id', '', '', ''])


def read_table(file_name: str):
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


def merge_tables(file1, file2):
    key_fields1: dict
    key_fields2: dict
    found_count = 0
    missing_count = 0
    item_count = 0

    table1, key_fields1, header = read_table(file1)
    table2, key_fields2, header = read_table(file2)


    pass

if __name__ == '__main__':
    file1 = "data_files/cdd-10.csv"
    file2 = "data_files/cdd-11-org.csv"
    able1, key_fields1, header1, table2, key_fields2, header2 = compare_tables(file1,file2)

    key_set1 = set(key_fields1.keys())
    key_set2 = set(key_fields2.keys())
    dif_2_1 = key_set2.difference(key_set1)
    dif_1_2 = key_set1.difference(key_set2)
    inter_1_2 = key_set1.intersection(key_set2)

    print(f"\n\nIntersection={len(inter_1_2)} 1=[{file1}] ^ 2=[{file2}] intersection = {inter_1_2}")
    print(f"\nDifference 1st-2nd={len(dif_1_2)} [{file1}] - 2=[{file2}]  diff={dif_1_2}")
    print(f"\nDifference 2nd-1st={len(dif_2_1)} [{file2}] - 1=[{file1}] diff= {dif_2_1}")