import os
import re
import sys
import traceback

from cdd_to_cts import static_data
from cdd_to_cts.static_data import find_url_re_str, java_methods_re_str, java_object_re_str, java_defines_str, \
    all_words_to_skip, CTS_SOURCE_PARENT


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
    traceback.print_exc()


def process_requirement_text(text_for_requirement_value: str, previous_value: str = None):
    value = cleanhtml(text_for_requirement_value)
    value = remove_n_spaces_and_commas(value)
    if previous_value:
        return '{} | {}'.format(previous_value, value)
    else:
        return value


def add_list_to_dict(new_value_to_add: str, dict_containing_values: dict, key: str, separator=' ', header: [] = static_data.cdd_to_cts_app_header) -> dict:
    possible_pre_existing_value = None
    if not new_value_to_add:
        return dict_containing_values
    if not header.index(key):
        raise_error(f"add_list_to_dict no key for [{key}] in {str(header)}")
    try:
        possible_pre_existing_value = dict_containing_values.get(key)
    except Exception as err:
        raise_error(f"failed to get key={key} from dict={str(dict_containing_values)} {str(err)}", err)

    if possible_pre_existing_value:
        dict_containing_values[key] = f'{possible_pre_existing_value}{separator}{new_value_to_add}'
    else:
        dict_containing_values[key] = new_value_to_add
    return dict_containing_values


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
    value = re.sub(",", ";", value)
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
    if file.find(prepend_path_if_needed) == -1:
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


def build_test_cases_module_dictionary(testcases_grep_results=static_data.TEST_CASE_MODULES,
                                       logging: bool = False) -> dict:
    test_cases_to_path: dict = dict()
    # ./tests/DropBoxManager/AndroidTest.xml:29:        <option name="test-file-name" value="CtsDropBoxManagerTestCases.apk" />
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
