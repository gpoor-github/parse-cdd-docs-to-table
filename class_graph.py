import re
import time


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


re_method = re.compile('(\w+?)\(\)')
re_class = re.compile('class (\w+)')


def parse_grep_of_at_test_files(results_grep_at_test: str = "input/test-files.txt"):
    test_files_to_methods: {str: str} = dict()

    re_annotations = re.compile('@Test.*?$')
    with open(results_grep_at_test, "r") as grep_of_test_files:
        file_content = grep_of_test_files.readlines()
        count = 0
        while count < len(file_content):
            line = file_content[count]
            count += 1
            result = re_annotations.search(line)
            # Skip lines without annotations
            if result:
                print("read {} :{}".format(count, result))
                test_annotated_file_name = line.split(":")[0]

                # requirement = result.group(0)
                line_method = file_content.pop()
                count += 1
                class_def, method = parse_(line_method)
                if class_def == "" and method == "":
                    line_method = file_content.pop()
                    count += 1
                    class_def, method = parse_(line_method)
                if method:
                    method_dict: {str: str} = test_files_to_methods.get(test_annotated_file_name)
                    if not method_dict:
                        method_dict = dict({method: 0})
                    else:
                        if method_dict.get(method):
                            method_dict[method] += 1
                        else:
                            method_dict[method] = 0
                    test_files_to_methods[test_annotated_file_name] = method_dict
                    print(f'{count}){test_annotated_file_name}:{method_dict}')
    return test_files_to_methods


def parse_(line_method):
    method_result = re_method.search(line_method)
    class_def = ""
    method = ""
    if method_result:
        method = method_result.group(0)
    else:
        class_result = re_class.search(line_method)
        if class_result:
            class_def = class_result.group(0)
    return class_def, method


def parse_dependency_file(file_name_in: str):
    # /Volumes/graham-ext/AndroidStudioProjects/cts
    input_file = open(file_name_in, 'r')
    test_classes_to_dependent_classes: dict = dict()
    file_as_string = input_file.read()
    file_splits = file_as_string.split('<file path=')
    target_file_name = "!Error target_file_name not found"
    for a_file_split in file_splits:
        target_file_name = re.search('\"(.+?)\"+?', a_file_split).group(
            0)  # .replace('$PROJECT_DIR$/tests/acceleration/Android.bp"')
        dependencies_split = a_file_split.split('<dependency path=')
        dependency_list: [] = list()
        for a_dependencies_split in dependencies_split:
            dependencies_file_name = re.search('\"(.+?)+\"', a_dependencies_split).group(0)
            dependency_list.append(dependencies_file_name)
        test_classes_to_dependent_classes[target_file_name] = dependency_list
    input_file.close()
    return test_classes_to_dependent_classes


if __name__ == '__main__':

 start = time.perf_counter()
 tests_files_methods = parse_grep_of_at_test_files()
 print(tests_files_methods)
 end = time.perf_counter()
 print(f'Took time {end - start:0.4f}sec ')
