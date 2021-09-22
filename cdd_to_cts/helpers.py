import os
import re
import sys
import traceback

from cdd_to_cts import static_data
from cdd_to_cts.static_data import find_url_re_str, java_methods_re_str, java_object_re_str, java_defines_str, \
    all_words_to_skip, CTS_SOURCE_PARENT


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
    value = re.sub("\s\s+", " ", value)
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
    file_string = re.sub("\s|;|{|:|,\n", " ", text)
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
