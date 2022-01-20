import csv
import json
import os
import re
from os.path import exists

import parser_constants
import path_constants

import parser_helpers
import table_ops
from cdd_to_cts import table_functions_for_release
from parser_helpers import find_valid_path



def filter_files_to_search(f):
    return f.endswith(".java") or f.endswith(".py") or f.endswith(".cpp") or f.endswith(".kt") or f.endswith(
        ".c")
class ReadSpreadSheet:
    def __init__(self,root_to_crawl=path_constants.CTS_SOURCE_ROOT):
        root_to_crawl=os.path.expanduser(root_to_crawl)
        if not os.path.exists(root_to_crawl):
            parser_helpers.raise_error_system_exit(f"Path [{root_to_crawl}] does not exist, so it can not be crawled")
        self.root_to_crawl = root_to_crawl
    section_id = ""
    req_id = ""

    file_dict = {}
    not_found_count = 0
    not_found_list = []
    file_name_to_result = dict()
    found_class_count = 0
    found_method_count = 0
    number_of_line = 0
    rows_with_found_methods = list()

    def crawl(self, logging=False):
        # /Volumes/graham-ext/AndroidStudioProjects/cts
        for directory, subdirlist, filelist in os.walk(self.root_to_crawl):
            if logging: print(directory)
            path = directory.replace(self.root_to_crawl, ".")
            for f in filelist:
                if filter_files_to_search(f):
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
        class_count = 0
        is_found_method = False
        table = []
        header = []
        self.crawl()
        ccd_csv_file_name = find_valid_path(ccd_csv_file_name)

        with open(ccd_csv_file_name, newline=parser_constants.table_newline) as csv_file:
            print("Opened {}".format(ccd_csv_file_name))
            csv_reader = csv.reader(csv_file, delimiter=parser_constants.table_delimiter,
                                    dialect=parser_constants.table_dialect)

            for row in csv_reader:
                try:
                    if csv_reader.line_num == 1:
                        print(f'Column names are {", ".join(row)}')
                        header = row
                        self.rows_with_found_methods.append(row)
                    else:
                        # print(f'\t{row[0]} row 1 {row[1]}  row 2 {row[2]}.')
                        table.append(row)
                        table_index = csv_reader.line_num-2
                        class_def_value = table[table_index][header.index(parser_constants.CLASS_DEF)]
                        method_value = table[table_index][header.index(parser_constants.METHOD)]
                        self.section_id = table[table_index][header.index(parser_constants.SECTION_ID)]
                        self.req_id = table[table_index][header.index(parser_constants.REQ_ID)]

                        # module_value = table[table_index][header.index("module")]
                        if class_def_value:
                            file_name = self.file_dict.get(class_def_value)
                            if not file_name:
                                for class_key in self.file_dict:
                                    file_name_in_dict = self.file_dict.get(class_key)
                                    if file_name_in_dict.find(class_def_value) > -1:
                                        file_name = file_name_in_dict

                            if file_name and exists(file_name):
                                self.found_class_count += 1
                                print(
                                    f' {self.found_class_count}) class name {class_def_value} class file {file_name} ')
                                is_found_method = self.check_for_file_and_method(file_name, method_value,
                                                                     self.file_name_to_result)
                            if is_found_method:
                                self.found_method_count += 1
                                self.rows_with_found_methods.append(row)
                                print(f'Found class and method {csv_reader.line_num } lines. ')

                            else:
                                self.not_found_count += 1

                except Exception as err:
                    parser_helpers.print_system_error_and_dump(f" Error index {table_index} {err}",err)
                    break
            csv_file.close()
            print("End for loop")
            print('No files {}'.format(self.not_found_count))
            print('Files {}'.format(self.found_method_count))
            return self.file_name_to_result, self.not_found_count, self.found_method_count

    # Method that takes file names in sheets and tries to find them.
    def check_for_file_and_method(self, file_name_from_class, method_value, file_name_to_result) -> bool:
        # file_name_from_class = "{}/tests/tests/{}.{}".format(CTS_SOURCE_ROOT,class_def_value.replace(".","/"),'java')
        method_value = method_value.strip('(').strip(')')

        if file_name_from_class:
            try:
                file_as_string = parser_helpers.read_file_to_string(file_name_from_class)
                # with open(file_name_from_class, "r") as f:
                #     file_as_string = f.read()
                test_re2 = "(\n\s*)(public|protected|private|static)+\s*[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*(\{?|[^;])"
                method_re_str = "(\n\s*:?)(public|protected|private|static)+\s*[\w\<\>\[\]]+\s+" + method_value + "\s*\([^\)]*\)\s*(\{?|[^;])"

                test_result = re.search(test_re2,file_as_string)
                method_index_re_result = re.search(method_re_str,file_as_string)
                method_index = method_index_re_result.start()
                if method_index > -1:
                    is_annotation_for_method_found = file_as_string.find('@CddTest', method_index - 200, method_index) > 0
                    if not is_annotation_for_method_found:
                        # No annotation inject one.
                        method_line_start_index = method_index
                        part_1 = file_as_string[:method_line_start_index]
                        part_2 = file_as_string[method_line_start_index:]
                        annotate_file = part_1 + f'\n    @CddTest(requirement="{self.section_id}/{self.req_id}")' + part_2
                        parser_helpers.write_file_to_string(file_name_from_class, annotate_file)


                    is_test_annotation_found = file_as_string.find('@Test', method_index - 100, method_index) > 0
                    if is_test_annotation_found:
                        file_name_to_result[
                            file_name_from_class] = method_value + ":Found and is @Tests supporting annotation"
                        return True
                    else:

                        file_name_to_result[
                            file_name_from_class] = method_value + ":Found but ,@Test annotation not found"
                else:
                    file_name_to_result[file_name_from_class] = method_value + ":Failed reason: Method not found"
            except Exception as err:
                print(" Could not open " + file_name_from_class)
                file_name_to_result[file_name_from_class] = method_value + " Failed reason: File not found " + str(err)
        return False


def test_does_class_ref_file_exist(root):
    all_cdd_12 ="/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/input/cdd_12_downloaded_mod_to_annotate.tsv"
    december_6 = "parse-cdd-docs-to-tablea1_working_12/find_annotations.tsv"
    foundish = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/output/found_rows.tsv"
    gpoor_map = "/home/gpoor/PycharmProjects/parse-cdd-docs-to-table/a1_working_12/done_of_155_manual.tsv"
    annotations = "../output/annotations_mappings.tsv"
    sample_known_good = "../a1_working_12/to_inject_methods.tsv"
    temp_file = "../output/temp_column_prune.tsv"
    table_functions_for_release.update_table_column_subset(sample_known_good,parser_constants.cdd_12_full_header_for_ref,temp_file)
    rs = ReadSpreadSheet(root)

    result_dict, not_found, found = rs.does_class_ref_file_exist(temp_file)
    print('results {}\n classes file found={} found_method={} not found={}'.format(json.dumps(result_dict, indent=4), rs.found_class_count, rs.found_method_count, rs.not_found_count))
    table_ops.write_table("../output/found_rows2.tsv",rs.rows_with_found_methods,None)
if __name__ == '__main__':
    test_does_class_ref_file_exist("~/cts-12-source/")

