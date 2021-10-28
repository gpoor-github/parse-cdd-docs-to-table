import csv
import os
import re

import rx

import helpers
import static_data
import table_ops
from helpers import find_valid_path
from static_data import CTS_SOURCE_ROOT


def check_for_file_and_method(file_name_from_class: str, method_value: str, file_name_to_result: dict) -> bool:
    # file_name_from_class = "{}/tests/tests/{}.{}".format(CTS_SOURCE_ROOT,class_def_value.replace(".","/"),'java')

    if file_name_from_class:
        try:
            with open(file_name_from_class, "r") as f:
                file_as_string = f.read()
                method_index = file_as_string.find(method_value.replace('()', ''))
                if method_index >= 0:
                    test_index = file_as_string.find('@Test', method_index - 100, method_index) >= 0
                    if file_as_string.index('@Test') >= 0 and ((test_index - method_index) < 100):
                        file_name_to_result[file_name_from_class] = method_value + " Found and is @Test"
                        return True
                    else:
                        file_name_to_result[
                            file_name_from_class] = method_value + " Failed reason: @Test annotation not found"
                else:
                    file_name_to_result[file_name_from_class] = method_value + " Failed reason: Method not found"
                f.close()
        except Exception as err:
            print(" Could not open " + file_name_from_class)
            file_name_to_result[file_name_from_class] = method_value + " Failed reason: File not found " + str(err)
    return False


class ReadSpreadSheet:
    file_dict = {}
    not_found_count = 0
    not_found_list = []
    file_name_to_result = dict()

    found_count = 0

    def crawl(self):
        # /Volumes/graham-ext/AndroidStudioProjects/cts
        for directory, subdirlist, filelist in os.walk(CTS_SOURCE_ROOT + "/tests/"):
            print(directory)
            path = directory.replace(CTS_SOURCE_ROOT, ".")
            for f in filelist:
                if f.endswith(".java"):
                    full_path = "{}/{}".format(directory, f)
                    # with open(full_path, 'r') as file:
                    #   file_string = file.read().replace('\n', '')
                    class_path = "{}/{}".format(path, f)
                    class_path = class_path.replace("/", ".").rstrip(".java")
                    split_path = class_path.split(".src.")
                    if len(split_path) > 1:
                        class_path = split_path[1]
                    self.file_dict[class_path] = full_path

    def does_class_ref_file_exist(self, ccd_csv_file_name):

        table = []
        header = []
        self.crawl()
        ccd_csv_file_name = find_valid_path(ccd_csv_file_name)

        with open(ccd_csv_file_name, newline=static_data.table_newline) as csv_file:
            print(f"Opened {ccd_csv_file_name}")
            csv_reader = csv.reader(csv_file, delimiter=static_data.table_delimiter, dialect=static_data.table_dialect)
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
                    # section_value = table[table_index][header.index("Section")]
                    # section_id_value = table[table_index][header.index(SECTION_ID)]
                    # req_id_value = table[table_index][header.index(REQ_ID)]
                    class_def_value = table[table_index][header.index(static_data.CLASS_DEF)]
                    method_value = table[table_index][header.index(static_data.METHOD)]
                    # module_value = table[table_index][header.index("module")]
                    if class_def_value:
                        is_found = check_for_file_and_method(self.file_dict.get(class_def_value), method_value,
                                                             self.file_name_to_result)
                        if is_found:
                            self.found_count += 1
                        else:
                            self.not_found_count += 1

                    line_count += 1
                    print(f'Processed {line_count} lines. ')
                print(f'For table {line_count}')
            csv_file.close()
            print("End for loop")
            print('No files {}'.format(self.not_found_count))
            print('Files {}'.format(self.found_count))
            return self.file_name_to_result, self.not_found_count, self.found_count

def observable_rows(table_file_name) -> rx.Observable:
    try:
        table_file_name = find_valid_path(table_file_name)

        with open(table_file_name, newline=static_data.table_newline) as csv_file:
            print(f"Opened {table_file_name}")
            csv_reader = csv.reader(csv_file, delimiter=static_data.table_delimiter,
                                    dialect=static_data.table_dialect)
            return rx.from_iterable(csv_reader)

    except IOError as e:
        helpers.raise_error(f"Failed to open file {table_file_name} exception -= {type(e)} exiting...")
        return rx.just(e)

def check_row_for_requirement_match(key:str, row:[], header:[str]):
    requirement_text = row[header.index[static_data.REQUIREMENT]]
    requirement_start = requirement_text[0:50]

    full_key = row[header.index[static_data.full_key_string_for_re]]
    results_section = re.findall(static_data.section_id_re_str, requirement_start)
    results_full = re.findall(static_data.full_key_string_for_re,requirement_start)
    results_req = re.findall(static_data.req_id_re_str,requirement_start)


    if len(results_full) > 0:
       if requirement_start.find(full_key) == -1:
           helpers.raise_error(f"Mismatch key and requirements: {full_key} {requirement_text} ")
    elif len(results_section) > 0:
        if requirement_start.find(full_key) == -1:
            helpers.raise_error(f"Mismatch key and requirements: {full_key} {requirement_text} ")
    elif len(results_req) > 0:
        if requirement_start.find(full_key) == -1:
            helpers.raise_error(f"Mismatch key and requirements: {full_key} {requirement_text} ")

def do_ids_match_requirements( ccd_csv_file_name):

    observable_rows(ccd_csv_file_name).pipe(rx.of()).subscribe(on_next= lambda key_row_tuple: check_row_for_requirement_match() )


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


def diff_tables_files(file_path1, file_path2):
    table1, _key_fields1, header1, duplicate_rows1 = table_ops.read_table_sect_and_req_key(file_path1)
    table2, _key_fields2, header2, duplicate_rows2 = table_ops.read_table_sect_and_req_key(file_path2)
    # table1, _key_fields1 = table_ops.remove_none_requirements(table1, _key_fields1)
    # table2, _key_fields2 = table_ops.remove_none_requirements(table2, _key_fields2)
    dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content = diff_tables(table1, _key_fields1,
                                                                                             table2, _key_fields2)

    file1 = os.path.basename(file_path1)
    file2 = os.path.basename(file_path2)
    report_diff(_key_fields1, _key_fields2, dif_1_2, dif_1_2_dict_content, dif_2_1, dif_2_1_dict_content,
                duplicate_rows1, duplicate_rows2, file1, file2, header1, header2, intersection)
    return dif_1_2, dif_2_1, intersection, dif_1_2_dict_content, dif_2_1_dict_content

def report_content_diff(_key_fields1, _key_fields2, dif_1_2_dict_content, dif_2_1_dict_content, file1, file2, header1, header2, intersection):

    print("\nDifferences in shared rows starts >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print(f"\nCompare shared rows 1st-2nd={len(dif_1_2_dict_content)} diff=[{dif_1_2_dict_content}]")
    print(
        f"Differences 1st-2nd={len(dif_1_2_dict_content)} above  f1=[{file1}] ^ f2=[{file2}] . can be long <<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>\n")
    print(f"\nCompare shared rows 2st-1nd={len(dif_2_1_dict_content)} diff= [{dif_2_1_dict_content}]")
    print("Differences in shared rows ends... can be long <<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>\n\n")
    print(f"\n\nIntersection={len(intersection)} =[{intersection}]")
    header_set1 = set(header1)
    header_set2 = set(header2)
    if (len(header_set1.difference(header_set2)) + len(header_set2.difference(header_set1))) ==0 :
        print(f"No Different  in headers f1=[{file1}]  f2=[{file2}]\n")
    else:
        print(
            f'Header dif1-2 [{header_set1.difference(header_set2)}] Header dif1-2 [{header_set2.difference(header_set1)}]'
            f'\nintersection=[{header_set1.intersection(header_set2)}]\n')
    print(f"\nSize of table_target={len(_key_fields1)} table_source={len(_key_fields2)} f1=[{file1}] ^ f2=[{file2}] ")
    print(
        f"Intersection of {len(intersection)}  content differs 1-2 {len(dif_1_2_dict_content)} and 2-1 {len(dif_2_1_dict_content)}  rows")

def report_diff(_key_fields1, _key_fields2, dif_1_2, dif_1_2_dict_content, dif_2_1, dif_2_1_dict_content,
                duplicate_rows1, duplicate_rows2, file1, file2, header1, header2, intersection):
    handle_duplicates(duplicate_rows1, duplicate_rows2, file1, file2)
    report_content_diff(_key_fields1,_key_fields2,dif_1_2_dict_content,dif_2_1_dict_content,file1,file2,header1,header2,intersection)
    report_key_diff(_key_fields1,_key_fields2,dif_1_2,dif_2_1,file1,file2)
    print(f"Difference 1st-2nd={len(dif_1_2)} 2st-1nd={len(dif_2_1)}  ")

def report_key_diff(_key_fields1, _key_fields2, dif_1_2, dif_2_1, file1, file2):
    print(f"\n Size of {file1}={len(_key_fields1)} {file2}={len(_key_fields2)} ")

    if len(dif_1_2) + len(dif_2_1) == 0:
        print(f"No KEY Different keys or headers {file1} and {file2}\n")
    else:
        print(f"\nA total of {len(dif_1_2)+len(dif_2_1)} req differ between {file1} and {file2}")
        print(f" {len(dif_1_2)} are in {file1} and not in {file2}")
        print(f" {len(dif_2_1)} are in {file2} and not in {file1}")
        print(f" {len(dif_1_2)} are in {file1} and not in {file2} \n Requirements ={dif_1_2}\n")
        print(f" {len(dif_2_1)} are in {file2} and not in {file1} \n Requirements ={dif_2_1}\n")

        print(f"Summary of requirements difference {file1}={len(_key_fields1)} {file2}={len(_key_fields2)}: ")
        print(f"A total of {len(dif_1_2) + len(dif_2_1)} req differ between {file1} and {file2} details above")


def diff_tables(table1, _key_fields1, table2, _key_fields2):
    key_set1 = set(_key_fields1.keys())
    key_set2 = set(_key_fields2.keys())
    intersection = key_set1.intersection(key_set2)
    dif_1_2 = key_set1.difference(key_set2)
    dif_2_1 = key_set2.difference(key_set1)
    dif_1_2_dict_row_content: [str, set] = dict()
    dif_2_1_dict_row_content: [str, set] = dict()

    for shared_key_to_table_index in intersection:
        i1 = _key_fields1.get(shared_key_to_table_index)
        i2 = _key_fields2.get(shared_key_to_table_index)
        dif_1_2_at_i1 = set(table1[i1]).difference(set(table2[i2]))
        if len(dif_1_2_at_i1) > 0:
            dif_1_2_dict_row_content[shared_key_to_table_index] = set(dif_1_2_at_i1)
        dif_2_1_at_i2 = set(table2[i2]).difference(set(table1[i1]))
        if len(dif_2_1_at_i2) > 0:
            dif_2_1_dict_row_content[shared_key_to_table_index] = set(dif_2_1_at_i2)

    return dif_1_2, dif_2_1, intersection, dif_1_2_dict_row_content, dif_2_1_dict_row_content


if __name__ == '__main__':
    rs = ReadSpreadSheet()
    cdd_11_before_gpoor = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_working/Working copy of CDD_CTS, CTS-V Annotation Tracker(8.1_9_10_11) go_cdd-cts-tracker - Before gpoor (2).csv"
    cdd_11 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/data_files/gpoor_final_completed_items_for_r.tsv"
    cdd_11_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/cdd_11_DATA_SOURCES_CSV_FROM_HTML_1st.tsv"
    cdd_12_with_sections ="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/DATA_SOURCES_cdd-12_CSV_FROM_HTML_1st.tsv"
    cdd_12_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/cdd_12_DATA_SOURCES_CSV_FROM_HTML_1st.tsv"
    annotation_12 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_working/mapping_output_for_import.tsv"
    cdd_12_to_do ="/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a_working/Differences between and CDD_11 and CDD12 - Requirements in CDD 12 but not in CDD-11 (1).tsv"
    # result_dict, not_found, found = rs.does_class_ref_file_exist(mapping_cdd)
    # print('results {}\n found={} not found={}'.format(json.dumps(result_dict, indent=4), rs.found_count, rs.not_found_count))
    diff_tables_files(cdd_11_created, cdd_12_created)
