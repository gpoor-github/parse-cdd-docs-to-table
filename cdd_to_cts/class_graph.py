import os
import re
import time

import persist
from cdd_to_cts import static_data_holder

FILES_TO_TEST_METHODS_PICKLE = "storage/test_files_to_methods.pickle"


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


def get_cached_grep_of_at_test_files(results_grep_at_test: str = FILES_TO_TEST_METHODS_PICKLE):
    local_tests_files_methods: dict = dict()
    try:
        local_tests_files_methods: dict = persist.read(results_grep_at_test)
    except IOError:
        print("Could not open test_files_to_methods, recreating ")
        test_files_to_methods = __parse_grep_of_at_test_files()
        persist.write(test_files_to_methods, results_grep_at_test)

    return local_tests_files_methods


def clear_cached_grep_of_at_test_files():
    try:
        global_tests_files_methods = None
        os.remove(FILES_TO_TEST_METHODS_PICKLE)
    except IOError:
        pass


def __parse_grep_of_at_test_files(results_grep_at_test: str = static_data_holder.TEST_FILES_TXT):
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
                test_annotated_file_name_absolute_path = line.split(":")[0]
                test_annotated_file_name = get_cts_root(test_annotated_file_name_absolute_path)
                # requirement = result.group(0)
                line_method = file_content.pop()
                count += 1
                class_def, method = parse_(line_method)
                if class_def == "" and method == "":
                    line_method = file_content.pop()
                    count += 1
                    class_def, method = parse_(line_method)
                if method:
                    if test_files_to_methods.get(test_annotated_file_name):
                        test_files_to_methods[
                            test_annotated_file_name] = f'{test_files_to_methods.get(test_annotated_file_name)} {method}'.strip(
                            ' ')
                    else:
                        test_files_to_methods[test_annotated_file_name] = method.strip(' ')

                print(f'{count}) {test_annotated_file_name}:{method}')
    print(f'{count}) {len(test_files_to_methods)}')
    return test_files_to_methods


def get_cts_root(test_annotated_file_name_absolute_path):
    test_annotated_file_name_split = test_annotated_file_name_absolute_path.split('/cts/', 1)
    test_annotated_file_name = f'cts/{test_annotated_file_name_split[1]}'
    return test_annotated_file_name


def parse_(line_method):
    method_result = re_method.search(line_method)
    class_def = str()
    method = str()
    if method_result:
        method = method_result.group(0)
    else:
        class_result = re_class.search(line_method)
        if class_result:
            class_def = class_result.group(0)
    return class_def, method


def parse_dependency_file(file_name_in: str = static_data_holder.INPUT_DEPENDENCIES_FOR_CTS_TXT):
    # /Volumes/graham-ext/AndroidStudioProjects/cts
    input_file = open(file_name_in, 'r')
    test_classes_to_dependent_classes: dict = dict()
    file_as_string = input_file.read()
    file_splits = file_as_string.split('<file path=')
    for a_file_split in file_splits:
        if dependencies_file_name.endswith('.java') and dependencies_file_name:
            target_file_name = re.search('\"(.+?)\"+?', a_file_split).group(0)  # .replace('$PROJECT_DIR$/tests/acceleration/Android.bp"')
        dependencies_split = a_file_split.split('<dependency path=')
        dependency_list: [] = list()
        for a_dependencies_split in dependencies_split:
            dependencies_file_name = re.search('\"(.+?)+\"', a_dependencies_split).group(0)
            if dependencies_file_name.endswith('.java') and dependencies_file_name:
                dependencies_file_name = dependencies_file_name.replace('$USER_HOME$','~/')
                dependency_list.append(dependencies_file_name)

        test_classes_to_dependent_classes[target_file_name] = dependency_list
    input_file.close()
    return test_classes_to_dependent_classes


if __name__ == '__main__':
    start = time.perf_counter()
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
