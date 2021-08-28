import csv


def read_table(file_name: str):
    table = []
    header = []
    key_fields: dict = dict()
    with open(file_name) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                header = row
                line_count += 1
            else:
                print(f'\t{row[0]} row 1 {row[1]}  row 2 {row[2]}.')
                table.append(row)
                table_index = line_count - 1
                # Section,section_id,req_id
                section_value = table[table_index][header.index("Section")]
                section_id_value = table[table_index][header.index("section_id")].rstrip('.')
                req_id_value = table[table_index][header.index("req_id")]
                class_def_value = table[table_index][header.index("class_def")]
                method_value = table[table_index][header.index("method")]
                module_value = table[table_index][header.index("module")]
                if len(req_id_value) > 0:
                    key_value = '{}/{}'.format(section_id_value, req_id_value)
                elif len(section_id_value) > 0:
                    key_value = section_id_value
                key_fields[key_value] = table_index
                line_count += 1
                print(f'Processed {line_count} lines {key_value} ')
            print(f'For table {line_count}')
        print("End for loop")
        return table, key_fields


def compare_tables(file1, file2):
    key_fields1: dict
    key_fields2: dict
    found_count = 0
    missing_count = 0
    item_count = 0

    table1, key_fields1 = read_table(file1)
    table2, key_fields2 = read_table(file2)

    key_set1 = set(key_fields1.keys())
    key_set2 = set(key_fields2.keys())
    dif_2_1 = key_set2.difference(key_set1)
    inter_2_1 = key_set2.intersection(key_set1)
    dif_1_2 = key_set1.difference(key_set2)
    inter_1_2 = key_set1.intersection(key_set2)
    print(f"\n\nDiff 1=[{file1}] vs 2=[{file2}] size={len(dif_1_2)} {dif_1_2}")
    print(f"Diff 2=[{file2}] vs 1=[{file1}] size={len(dif_2_1)} {dif_2_1}")

    pass


if __name__ == '__main__':
    compare_tables("CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - CDD 11.csv",
                                   "created_output.csv")
