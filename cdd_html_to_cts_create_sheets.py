import os
import random
import re
import time

import data_sources
import sourcecrawlerreducer
from comparesheets import read_table
from update_table import write_table, update_table, default_header, merge_header, new_header

REQUIREMENTS_FROM_HTML_FILE = 'input/Android 11 Compatibility Definition_no_section_13.html'
TABLE_FILE_NAME = 'input/new_recs_remaining_todo.csv'


def build_test_cases_module_dictionary(testcases_grep_results) -> dict:
    test_cases_to_path: dict = dict()

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
        path_split = path.split("tests/", 1)
        path = path_split[1]
        path = path.replace("/", ".")

        value = split_line[2]
        re_value = re.search("(\w+)TestCases", value)
        if re_value:
            test_case_name = re_value[0]
            test_cases_to_path[path] = test_case_name
    return test_cases_to_path


def find_urls(text_to_scan_urls: str):
    find_url_re_str = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return " ".join(set(re.findall(find_url_re_str, text_to_scan_urls)))


# find likely java objects from a text block
def find_java_objects(text_to_scan_for_java_objects: str):
    java_objects = set()

    java_objects.update(cleanhtml(process_requirement_text(text_to_scan_for_java_objects)).split(' '))
    java_objects = sourcecrawlerreducer.remove_non_determinative_words(java_objects)
    java_methods_re_str = '(?:[a-zA-Z]\w+\( ?\w* ?\))'
    java_objects.update(re.findall(java_methods_re_str, text_to_scan_for_java_objects))

    java_object_re_str = '(?:[a-zA-Z]\w+\.)+[a-zA-Z_][a-zA-Z]+'
    java_objects.update(re.findall(java_object_re_str, text_to_scan_for_java_objects))

    java_defines_str = '[A-Z][A-Z0-9]{2,20}[_A-Z0-9]{0,40}'
    java_objects.update(re.findall(java_defines_str, text_to_scan_for_java_objects))

    java_objects = sourcecrawlerreducer.remove_non_determinative_words(java_objects)
    if len(java_objects) > 0:
        return " ".join(java_objects)
    else:
        return None


def process_requirement_text(text_for_requirement_value: str, previous_value: str = None):
    value = cleanhtml(text_for_requirement_value)
    value = re.sub("\s\s+", " ", value)
    value = re.sub(",", ";", value)
    if previous_value:
        return '{} | {}'.format(previous_value, value)
    else:
        return value


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def clean_html_anchors(raw_html: str):
    return raw_html.replace("</a>", "")


def handle_java_files_data(key_str):
    # keys_to_files_dict = data_sources.files_to_words
    files_to_method_calls = data_sources.files_to_method_calls
    files_to_test_cases = data_sources.files_to_test_cases
    at_test_files_to_methods = data_sources.at_test_files_to_methods

    keys_to_files_dict = sourcecrawlerreducer.search_files_for_words(key_str)
    # keys_to_files_dict1 = sorted(keys_to_files_dict.items(), key=lambda x: x[1], reverse=True)
    a_single_test_file_name: str = ""
    test_case_name: str = ""
    class_name: str = ""

    if keys_to_files_dict:
        # filenames_str = keys_to_files_dict.get(key_str)
        found_methods = None
        file_name = None
        a_method = None
        found_methods_string = None
        if keys_to_files_dict:
            # TODO just handling one file for now! Needs to change.

            for file_name in keys_to_files_dict:
                a_single_test_file_name = file_name
                found_methods_string = at_test_files_to_methods.get(file_name)
                if found_methods_string:
                    break
            if found_methods_string:
                # A better single file name :)
                a_single_test_file_name = file_name
                found_methods = found_methods_string.split(' ')
                if len(found_methods)>0:
                    a_method = found_methods[random.randrange(0,len(found_methods))]

            class_name_split_src = a_single_test_file_name.split('/src/')
            # Module
            if len(class_name_split_src) > 0:
                test_case_split = str(class_name_split_src[0]).split('/cts/tests/')
                if len(test_case_split) > 1:
                    project_root = str(test_case_split[1]).replace("/", ".")
                    test_case_name = files_to_test_cases.get(project_root)

            if len(class_name_split_src) > 1:
                class_name = str(class_name_split_src[1]).replace("/", ".").rstrip(".java")

        return a_single_test_file_name, test_case_name, a_method, class_name
    return None, None, None, None


def create_populated_table(keys_to_find_and_write):
    table: [[str]] = []
    keys_to_table_index: dict[str, int] = dict()
    table_row_index = 0
    for temp_key in keys_to_find_and_write:
        key_str: str = temp_key
        key_str = key_str.rstrip(".").strip(' ')
        write_new_data_line_to_table(key_str, data_sources.key_to_full_requirement_text, table,
                                     table_row_index)  # test_file_to_dependencies)
        keys_to_table_index[key_str] = table_row_index
        table_row_index += 1
    return table, keys_to_table_index


# Section,section_id,req_id,Test Availability,Annotation? ,New Req for R?,New CTS for R?,class_def,method,module,
# ['Section', 'section_id', 'req_id', 'Test Availability','class_def', 'method', 'module','full_key','requirement', 'key_as_number','search_terms','urls','file_name'])

def write_new_data_line_to_table(key_str: str, keys_to_sections: dict, table: [[str]], table_row_index: int):
    key_to_java_objects = data_sources.key_to_java_objects
    key_to_urls = data_sources.key_to_urls
    section_data = keys_to_sections.get(key_str)
    if len(table) <= table_row_index:
        table.append(['', '', '', '', '', '', '', '',
                      '', '', '', '', ''])

    print(f"keys from  {table_row_index} [{key_str}]")
    key_str = key_str.rstrip(".").strip(' ')
    key_split = key_str.split('/')
    table[table_row_index][new_header.index('section_id')] = key_split[0]

    table[table_row_index][new_header.index('full_key')] = key_str
    section_data_cleaned = '"{}"'.format(section_data.replace("\n", " "))
    table[table_row_index][new_header.index('requirement')] = section_data_cleaned

    if len(key_split) > 1:
        table[table_row_index][new_header.index('req_id')] = key_split[1]
        table[table_row_index][new_header.index('key_as_number')] = convert_version_to_number(key_split[0],
                                                                                              key_split[1])
        table[table_row_index][new_header.index('urls')] = key_to_urls.get(key_str)
        table[table_row_index][new_header.index('search_terms')] = key_to_java_objects.get(key_str)
        a_single_test_file_name, test_case_name, a_method, class_name = handle_java_files_data(key_str)

        table[table_row_index][new_header.index('module')] = test_case_name
        if a_single_test_file_name:
            table[table_row_index][new_header.index('class_def')] = class_name
            table[table_row_index][new_header.index('file_name')] = a_single_test_file_name
        if a_method:
            table[table_row_index][new_header.index('method')] = a_method
        # table[table_row_index][new_header.index('Test Available')] = "Test Available"

    else:
        table[table_row_index][new_header.index('key_as_number')] = convert_version_to_number(key_split[0])
        print(f"Only a major key? {key_str}")


def convert_version_to_number(section_id: str, requirement_id: str = '\0-00-00'):
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

    return f'"{section_as_number}.{requirement_as_number}"'


def process_section(record_key_method, key_string_for_re, section_id, key_to_full_requirement_text,
                    key_to_java_objects, key_to_urls,
                    record_id_splits, section_id_count, total_requirement_count):
    record_id_count = 0
    for record_id_split in record_id_splits:
        key = record_key_method(key_string_for_re, record_id_split, section_id)
        if key:
            key_to_urls[key] = find_urls(record_id_split)
            these_java_objects = find_java_objects(record_id_split)
            if these_java_objects:
                key_to_java_objects[key] = these_java_objects
            key_to_full_requirement_text[key] = process_requirement_text(record_id_split,
                                                                         key_to_full_requirement_text.get(
                                                                             key))
            record_id_count += 1
            total_requirement_count += 1
            print(
                f'key [{key}] {key_string_for_re} value [{key_to_full_requirement_text.get(key)}] section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} ')
    return total_requirement_count


def build_composite_key(key_string_for_re, record_id_split, section_id):
    record_id_result = re.search(key_string_for_re, record_id_split)
    if record_id_result:
        record_id = record_id_result[0].rstrip(']')
        return '{}/{}'.format(section_id, record_id)
    else:
        return None


def find_full_key(key_string_for_re, record_id_split, section_id):
    record_id_result = re.search(key_string_for_re, record_id_split)
    if record_id_result:
        record_id_string = record_id_result[0]

        return record_id_string.rstrip(']').lstrip('>')
    else:
        return None


def parse_cdd_html_to_requirements(cdd_html_file=REQUIREMENTS_FROM_HTML_FILE):
    key_to_full_requirement_text = dict()
    key_to_java_objects = dict()
    key_to_urls = dict()
    # Should do key_to_cdd_section = dict()
    keys_not_found: list = []
    total_requirement_count = 0
    with open(cdd_html_file, "r") as text_file:
        cdd_requirements_file_as_string = text_file.read()
    cdd_requirements_file_as_string = clean_html_anchors(cdd_requirements_file_as_string)
    section_id_re_str: str = '"(?:\d{1,3}_)+'
    cdd_sections_splits = re.split('(?={})'.format(section_id_re_str), cdd_requirements_file_as_string, flags=re.DOTALL)
    section_id_count = 0
    for section in cdd_sections_splits:
        cdd_section_id_search_results = re.search(section_id_re_str, section)
        if not cdd_section_id_search_results:
            continue
        cdd_section_id = cdd_section_id_search_results[0]
        cdd_section_id = cdd_section_id.replace('"', '').rstrip('_')
        cdd_section_id = cdd_section_id.replace('_', '.')
        if '13' == cdd_section_id:
            # section 13 is "Contact us" and has characters that cause issues at lest for git
            print(f"Warning skipping section 13 {section}")
            continue
        key_to_full_requirement_text[cdd_section_id] = process_requirement_text(section, None)
        composite_key_string_re = "\s*(?:<li>)?\["
        req_id_re_str = '(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?'
        full_key_string_for_re = '>(?:[0-9]{1,3}.)*[0-9]?[0-9]/' + req_id_re_str
        req_id_splits = re.split('(?={})'.format(full_key_string_for_re), section)
        total_requirement_count = process_section(find_full_key, full_key_string_for_re, cdd_section_id,
                                                  key_to_full_requirement_text,
                                                  key_to_java_objects, key_to_urls, req_id_splits,
                                                  section_id_count, total_requirement_count)
        # Only build a key if you can't find any...
        if len(req_id_splits) < 2:
            req_id_splits = re.split(composite_key_string_re, str(section))

            total_requirement_count = process_section(build_composite_key, req_id_re_str, cdd_section_id,
                                                      key_to_full_requirement_text,
                                                      key_to_java_objects, key_to_urls, req_id_splits,
                                                      section_id_count, total_requirement_count)

        section_id_count += 1
    return key_to_full_requirement_text, key_to_java_objects, key_to_urls, cdd_requirements_file_as_string


def cdd_html_to_cts_create_sheets(targets: str = 'all'):
    table, keys_from_table, header = read_table(TABLE_FILE_NAME)
    if targets == 'new' or targets == 'all':
        # Write New Table
        table_for_sheet, keys_to_table_indexes = create_populated_table(
            data_sources.key_to_full_requirement_text.keys())
        write_table('output/created_output.csv', table_for_sheet, new_header)
    else:
        table_for_sheet, keys_to_table_indexes = create_populated_table(keys_from_table)  # Just a smaller table
    if targets == 'append' or targets == 'all':
        # Write Augmented Table
        updated_table, misskey_key1, misskey_key2 = update_table(table, keys_from_table, header, table_for_sheet,
                                                                 keys_to_table_indexes, new_header, merge_header)
        write_table('output/updated_table.csv', updated_table, header)

    print(
        f'keys missing 1  {misskey_key1} keys missing 2 {misskey_key2}\nkeys1 missing  {len(misskey_key1)} keys2 missing {len(misskey_key2)} of {len(updated_table)}')


if __name__ == '__main__':
    start = time.perf_counter()
    cdd_html_to_cts_create_sheets('all')
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
