import os
import re
import sys
import traceback
from typing import Any

from cdd_to_cts import static_data
from cdd_to_cts.static_data import find_url_re_str, java_methods_re_str, java_object_re_str, java_defines_str, \
    all_words_to_skip, CTS_SOURCE_PARENT
from stackdump import stackdump


def get_list_void_public_test_files(results_grep_public_test: str = "input_scripts/public_void_test_files.txt") -> set:
    results_grep_public_test = find_valid_path(results_grep_public_test)
    test_file_set = set()

    try:
        with open(results_grep_public_test, "r") as grep_of_test_files:
            file_content = grep_of_test_files.readlines()
            count = 0
            while count < len(file_content):
                line = file_content[count]
                count += 1
                test_file_set.add( line.split(":")[0])
        grep_of_test_files.close()
    except FileNotFoundError as e:
        raise_error(f" Could not find {results_grep_public_test} ", e)
    return test_file_set


def convert_version_to_number_from_full_key(full_key: str):
    key_split = full_key.split('/')
    if len(key_split) == 1:
        return convert_version_to_number(key_split[0], '0.0.0')
    else:
        return convert_version_to_number(key_split[0], key_split[1])


def convert_version_to_number(section_id: str, requirement_id: str):
    section_splits = section_id.split(".")
    section_as_number = ''
    for i in range(4):
        if i < len(section_splits):
            idx = 0
            for j in range(1, -1, -1):
                if j >= len(section_splits[i]):
                    section_as_number += '0'
                else:
                    section_as_number += section_splits[i][idx]
                    idx += 1
        else:
            section_as_number += "00"

    requirement_splits = requirement_id.split("-")
    requirement_as_number = f'{ord(requirement_splits[0][-1])}'
    for k in range(1, len(requirement_splits)):
        if len(requirement_splits[k]) > 1:
            requirement_as_number = f'{requirement_as_number}{requirement_splits[k]}'
        else:
            requirement_as_number = f'{requirement_as_number}0{requirement_splits[k]}'

    return f'{section_as_number}.{requirement_as_number}'


def raise_error(message: str = "ERROR.. default cdd parser message.", a_exception: BaseException = None):
    print(message, file=sys.stderr)
    if a_exception:
        print(str(a_exception), file=sys.stderr)
    stackdump(message)
    traceback.print_exc()


def process_requirement_text(text_for_requirement_value: str, previous_value: str = None):
    value = cleanhtml(text_for_requirement_value)
    value = remove_n_spaces_and_commas(value)
    if previous_value:
        return '{} | {}'.format(previous_value, value)
    else:
        return value


def add_list_to_count_dict(new_value_to_add: Any, dictionary_with_existing_values: dict, key: str) -> dict:
    pre_existing_value = None
    if not new_value_to_add:
        return dictionary_with_existing_values
    try:
        pre_existing_value = dictionary_with_existing_values.get(key)
    except Exception as err:
        raise_error(f"failed to get key={key} from dict={str(dictionary_with_existing_values)} {str(err)}", err)

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
        raise_error(f"add_list_to_dict no key for [{key}] in {str(header)}")
    try:
        pre_existing_value = dictionary_with_existing_values.get(key)
    except Exception as err:
        raise_error(f"failed to get key={key} from dict={str(dictionary_with_existing_values)} {str(err)}", err)

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
            raise_error(f"Bad type add_to_count_dict {new_value_to_add}")

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


def find_section_id(section: str) -> str:
    cdd_section_id_search_results = re.search(static_data.SECTION_ID_RE_STR, section)
    if cdd_section_id_search_results:
        cdd_section_id = cdd_section_id_search_results[0]
        cdd_section_id = cdd_section_id.replace('"', '').rstrip('_')
        cdd_section_id = cdd_section_id.replace('_', '.')
        return cdd_section_id
    return ""


def remove_n_spaces_and_commas(value):
    value = re.sub("\\s\\s+", " ", value)
    value = re.sub(static_data.table_delimiter, " ", value)
    return value


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def clean_html_anchors(raw_html: str):
    return raw_html.replace("</a>", "")


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


def read_file_to_string(file: str, prepend_path_if_needed: str = CTS_SOURCE_PARENT):
    full_path = file
    if not file.startswith('/') and file.find(prepend_path_if_needed) == -1:
        full_path = prepend_path_if_needed + file

    with open(full_path, "r") as text_file:
        file_string_raw = text_file.read()
        file_string = re.sub(' Copyright.+limitations under the License', "", file_string_raw, flags=re.DOTALL)
        text_file.close()
        return file_string


def build_composite_key(key_string_for_re, record_id_split, section_id):
    record_id_result = re.search(key_string_for_re, record_id_split)
    if record_id_result:
        record_id = record_id_result[0].rstrip(']')
        return '{}/{}'.format(section_id, record_id)
    else:
        return None


def find_full_key(key_string_for_re, record_id_split, section_id=None):
    record_id_result = re.search(key_string_for_re, record_id_split)
    if record_id_result:
        record_id_string = record_id_result[0]

        return record_id_string.rstrip(']').lstrip('>')
    else:
        return None


def find_valid_path(file_name: str) -> str:

    if file_name.find(static_data.WORKING_ROOT[0:10]) != -1:
        return file_name

    if file_name.find(static_data.WORKING_ROOT) == -1:
        if not static_data.WORKING_ROOT.endswith('/') and not file_name.startswith('/'):
            file_name = static_data.WORKING_ROOT + '/' + file_name
        else:
            file_name = static_data.WORKING_ROOT + file_name
    return file_name


def build_test_cases_module_dictionary(testcases_grep_results=static_data.TEST_CASE_MODULES,
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
            path_split = path.split("tests/", 1)
            path = path_split[1]
            path = path.replace("/", ".")

            value = split_line[2]
            re_value = re.search("(\w+)TestCases", value)
            if re_value:
                test_case_name = re_value[0]
                test_cases_to_path[path] = test_case_name

    except Exception as e:
        raise_error(f"Error open file {testcases_grep_results}", e)
    return test_cases_to_path
