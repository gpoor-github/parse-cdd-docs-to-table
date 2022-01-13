import os
import re

#
# def get_package_name(file_name):
#     current_file = open(file_name, "r")
#     while True:
#         line = current_file.readline()
#         resutl = re.search("package\s+[a-z][a-z0-9_]*(\.[a-z0-9_]+)+[0-9a-z_]*", line)
#         if resutl:
#             break
#         # Skip lines without annotations
#     pass
import path_constants


def get_package_name(class_path):
    class_path = class_path.replace("/", ".").rstrip(".java")
    split_path = class_path.split(".src.")
    if len(split_path) > 1:
        class_path = split_path[1]
    return class_path


def test_case_name(path, testcase_dictionary: dict):
    split_path = path.split("/cts/")
    if len(split_path) > 1:
        root_path = split_path[1]
        root_path = root_path.replace("/", ".")
        split_path = root_path.split(".src.")
        if len(split_path) > 0:
            parent = split_path[0]
            module = testcase_dictionary.get(parent)
            return module
    return None


def build_test_cases_module_dictionary(testcases_grep_results):
    testCasesToPath: dict = {"": ""}

    with open(testcases_grep_results, "r") as f:
        file_content = f.readlines()

    count = 0
    # Strips the newline character
    for line in file_content:
        count += 1
        print("Line{}: {}".format(count, line.strip()))
        # ./tests/DropBoxManager/AndroidTest.xml:29:        <option name="test-file-name" value="CtsDropBoxManagerTestCases.apk" />
        split_line = line.split(":")
        file_and_path = split_line[0]
        path: str = os.path.dirname(file_and_path)
        path_split = path.split("cts/", 1)
        path = path_split[1]
        path = path.replace("/", ".")

        value = split_line[2]
        re_value = re.search("(\w+)TestCases", value)
        if re_value:
            test_case_name = re_value[0]
            testCasesToPath[path] = test_case_name
    return testCasesToPath


class ProcessAnnotationReferences:
    re_annotations = re.compile('@CddTest(\s*)\((\s*)requirement(\s*)=(\s*)"(.*?)\)')

    re_method = re.compile('(\w+?)\(\)')
    re_class = re.compile('class (\w+)')

    Section = ""
    section_id = "id unknown"
    req_id = "req_id unknown"
    status = "Test Available"
    class_def = "class_def unknown"
    method = "method unknown"
    module = "module unknown"
    Comment = ""
    Bug = ""
    file_name = ""

    # Section ,id,req_id,status,class_def,method,module,Comment,Bug
    # 2.2.1 Hardware(HandHeld),7.1.1,H-0-1,Test Available,android.dpi.cts.ConfgurationTest,testScreenConfigurateion,CtsDpiTestCases,,

    def parse_data(self):
        testCasesToPath = build_test_cases_module_dictionary("../input_data_from_cts/testcases-modules.txt")
        # /Volumes/graham-ext/AndroidStudioProjects/cts
        input_file = open('../input_data_from_cts/cdd_annotations_found.txt', 'r')
        output_file = open(path_constants.ANNOTATIONS_MAPPING_FOUND_IN_CTS_SOURCE, 'w')

        # Section ,id,req_id,status,class_def,method,module,Comment,Bug
        output_file.write(
            'Section\tsection_id\treq_id\tTest Available\tclass_def\tmethod\tmodule\tfile_name\tAnnotation?\tComment\tBug\t\n')

        template_string: str = "{Section}\t{section_id}\t{req_id}\t{status}\t{class_def}\t{method}\t{module}\t{file_name}\t{Annotation}\t{Comment}\t{Bug}\t\n"
        count = 0

        while True:
            self.initialize_values()
            line = input_file.readline()
            if not line:
                break
            result = self.re_annotations.search(line)
            # Skip lines without annotations
            if result:
                count += 1
                print("read {} :{}".format(count, result))
                self.file_name = line.split(":")[0]
                requirement = result.group(0)
                requirement = requirement.split("=")[1].strip(" \")][")
                id_and_req_id = requirement.split('/')
                self.section_id = id_and_req_id[0]
                req_ids = None
                if len(id_and_req_id) > 1:
                    self.req_id = id_and_req_id[1]
                    req_ids = id_and_req_id[1].split(',')
                    # self.req_id = "\"{req_id}\"".format(req_id=self.req_id)
                line_method = input_file.readline()
                self.class_def, self.method = self.parse_(line_method)
                if self.class_def == "" and self.method == "":
                    line_method = input_file.readline()
                    self.class_def, self.method = self.parse_(line_method)
                # Override class def a little weird.... but for now
                self.class_def = get_package_name(self.file_name)
                self.module = test_case_name(self.file_name, testCasesToPath)

                if req_ids:
                    for req_id_local in req_ids:
                        # "Section ,id,req_id,status,class_def,method,module,Comment,Bug
                        req_id_local = req_id_local.strip(" \")][")
                        line_out = template_string.format(Section=self.Section, section_id=self.section_id,
                                                          req_id=req_id_local,
                                                          status=self.status,
                                                          class_def=self.class_def, method=self.method,
                                                          module=self.module,
                                                          Comment=self.Comment,
                                                          Bug=self.Bug,
                                                          file_name=self.file_name,
                                                          Annotation="True")

                        print(line_out)
                        output_file.write(line_out)
                else:
                    line_out = template_string.format(Section=self.Section, section_id=self.section_id,
                                                      req_id="",
                                                      status=self.status,
                                                      class_def=self.class_def, method=self.method,
                                                      module=self.module,
                                                      Comment=self.Comment,
                                                      Bug=self.Bug,
                                                      file_name=self.file_name,
                                                      Annotation="True")
                    print("Line {}: result={}".format(count, line_out))
                    output_file.write(line_out)
            else:
                print("Skipped: " + line)

        input_file.close()
        output_file.close()

    def initialize_values(self):
        # Leave preview section self.Section = "Section unknown"
        self.section_id = "id unknown"
        self.req_id = "req_id unknown"
        self.status = "Test Available"
        self.class_def = "class_def unknown"
        self.method = "method unknown"
        self.module = "module unknown"
        self.Comment = "Comment unknown"
        self.Bug = "Bug unknown"

    def parse_(self, line_method):
        method_result = self.re_method.search(line_method)
        class_def = ""
        method = ""
        if method_result:
            method = method_result.group(0)
        else:
            class_result = self.re_class.search(line_method)
            if class_result:
                class_def = class_result.group(0)
        return class_def, method


if __name__ == '__main__':
    ProcessAnnotationReferences().parse_data()
