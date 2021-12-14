#  Block to comment

import os
import re
from typing import Any

import parser_constants
import static_data
from parser_helpers import print_system_error_and_dump, read_file_to_string, find_valid_path
from static_data import find_url_re_str, java_methods_re_str, java_object_re_str, java_defines_str, all_words_to_skip


def is_has_upper(target_string : str)-> bool:
    return any(ele.isupper() for ele in target_string)


def add_list_to_count_dict(new_value_to_add: Any, dictionary_with_existing_values: dict, key: str) -> dict:
    pre_existing_value = None
    if not new_value_to_add:
        return dictionary_with_existing_values
    try:
        pre_existing_value = dictionary_with_existing_values.get(key)
    except Exception as err:
        print_system_error_and_dump(f"failed to get key={key} from dict={str(dictionary_with_existing_values)} {str(err)}", err)

    if not pre_existing_value:
        dictionary_with_existing_values[key] = CountDict()
    if isinstance(dictionary_with_existing_values.get(key), CountDict):
        count_dict: CountDict = dictionary_with_existing_values[key]
        count_dict.add_to_count_dict(new_value_to_add)

    return dictionary_with_existing_values


def add_list_to_dict(new_value_to_add: Any, dictionary_with_existing_values: dict, key: str, separator=' ',
                     header: [] = static_data.cdd_to_cts_app_header) -> dict:
    pre_existing_value = None
    if not new_value_to_add:
        return dictionary_with_existing_values
    if not header.index(key):
        print_system_error_and_dump(f"add_list_to_dict no key for [{key}] in {str(header)}")
    try:
        pre_existing_value = dictionary_with_existing_values.get(key)
        if isinstance(pre_existing_value,str) and isinstance(new_value_to_add,str):
            if pre_existing_value.index(new_value_to_add) > -1:
                return dictionary_with_existing_values
    except Exception as err:
        print_system_error_and_dump(f"failed to get key={key} from dict={str(dictionary_with_existing_values)} {str(err)}", err)

    if pre_existing_value:
        if isinstance(pre_existing_value, str) and isinstance(new_value_to_add, str):
            new_value_to_add = new_value_to_add.strip()
            pre_existing_value = pre_existing_value.strip()
            dictionary_with_existing_values[key] = f'{pre_existing_value}{separator}{new_value_to_add}'
        elif isinstance(pre_existing_value, set) and isinstance(new_value_to_add, set):
            dictionary_with_existing_values[key] = new_value_to_add.union(pre_existing_value)
        elif isinstance(pre_existing_value, list):
            pre_existing_value.append(new_value_to_add)
        else:
            dictionary_with_existing_values[
                key] = f'{str(pre_existing_value)}{separator}{str(new_value_to_add)}'
    else:
        dictionary_with_existing_values[key] = new_value_to_add
    return dictionary_with_existing_values


class CountDict:
    def __init__(self):
        self.count_value_dict = dict()

    def add_to_count_dict(self, new_value_to_add: Any) -> dict[str, int]:
        current_count = 0
        if not new_value_to_add:
            return self.count_value_dict

        if isinstance(new_value_to_add, str):
            new_value_to_add = new_value_to_add.strip()
            if self.count_value_dict.get(new_value_to_add):
                current_count = self.count_value_dict.get(new_value_to_add)
            self.count_value_dict[new_value_to_add] = current_count + 1
        elif isinstance(new_value_to_add, list) or isinstance(new_value_to_add, set):
            for value in new_value_to_add:
                self.add_to_count_dict(value)
        else:
            print_system_error_and_dump(f"Bad type add_to_count_dict {new_value_to_add}")

        return self.count_value_dict


def find_urls(text_to_scan_urls: str):
    return " ".join(set(re.findall(find_url_re_str, text_to_scan_urls)))


def find_java_objects(text_to_scan_for_java_objects: str) -> set:
    java_objects = set()
    #  java_objects.update(cleanhtml(process_requirement_text(text_to_scan_for_java_objects)).split(' '))
    java_objects.update(re.findall(java_methods_re_str, text_to_scan_for_java_objects))
    java_objects.update(re.findall(java_object_re_str, text_to_scan_for_java_objects))
    java_objects.update(re.findall(java_defines_str, text_to_scan_for_java_objects))
    java_objects = remove_non_determinative_words(java_objects)
    java_objects.discard(None)
    return java_objects


def remove_non_determinative_words(set_to_diff: set):
    return set_to_diff.difference(all_words_to_skip)


def bag_from_text(text: str):
    file_string = re.sub("\\s|;|{|:|,\n", " ", text)
    split = file_string.split(" ")
    return set(split)


def make_files_to_string(iterable_file_list: [str]) -> str:
    flist: [str] = list()
    for file in iterable_file_list:
        flist.append(f'{file} ')
        flist.append(read_file_to_string(file))
    return " ".join(flist)


def build_test_cases_module_dictionary(testcases_grep_results=parser_constants.TEST_CASE_MODULES,
                                       logging: bool = False) -> dict:
    test_cases_to_path: dict = dict()
    # ./tests/DropBoxManager/AndroidTest.xml:29:        <option name="test-file-name"
    # value="CtsDropBoxManagerTestCases.apk" />
    testcases_grep_results = find_valid_path(testcases_grep_results)

    with open(testcases_grep_results, "r") as f:
        file_content = f.readlines()

    count = 0
    try:
        # Strips the newline character
        for line in file_content:
            if logging: print("Line{}: {}".format(count, line.strip()))
            split_line = line.split(":")
            file_and_path = split_line[0]
            path: str = os.path.dirname(file_and_path)
            path = path.removeprefix(parser_constants.CTS_SOURCE_ROOT)
            path = path.replace("/", ".").strip('.')

            value = split_line[2]
            re_value = re.search("(\w+)TestCases", value)
            if re_value:
                test_case_name = re_value[0]
                test_cases_to_path[path] = test_case_name

    except Exception as e:
        print_system_error_and_dump(f"Error open file {testcases_grep_results}", e)
    return test_cases_to_path


def filter_files_to_search(f):
    return f.endswith(".java") or f.endswith(".py") or f.endswith(".cpp") or f.endswith(".kt") or f.endswith(
        ".c")