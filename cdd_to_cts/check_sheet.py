import csv
import json
import os

from static_data_holder import CTS_SOURCE_ROOT


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

        except:
            print(" Could not open " + file_name_from_class)
            file_name_to_result[file_name_from_class] = method_value + " Failed reason: File not found"
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

    def parse_data(self, ccd_csv_file_name):
        # sheet_file = open('CDD11_CTS.tsv')
        # for line in sheet_file:
        #     print(line)
        table = []
        header = []
        self.crawl()
        with open(ccd_csv_file_name) as csv_file:
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
                    section_id_value = table[table_index][header.index("section_id")]
                    req_id_value = table[table_index][header.index("req_id")]
                    class_def_value = table[table_index][header.index("class_def")]
                    method_value = table[table_index][header.index("method")]
                    module_value = table[table_index][header.index("module")]
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
            print("End for loop")
            print('No files {}'.format(self.not_found_count))
            print('Files {}'.format(self.found_count))
            return self.file_name_to_result


if __name__ == '__main__':
    rs = ReadSpreadSheet()
    result: dict = rs.parse_data('input/created_output.csv')
    print('results {}\n found={} not found={}'.format(json.dumps(result, indent=4), rs.found_count, rs.not_found_count))
