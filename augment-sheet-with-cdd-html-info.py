import csv
import os
import re
import time

import class_graph
import persist
import sourcecrawlerreducer


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


def find_test_files(reference_diction: dict):
    # traverse root directory, and list directories as dirs and files as files
    collected_value: dict = dict()
    value_matched: dict = dict()
    count = 0
    start_time_file_crawl = time.perf_counter()
    # tests/tests/widget/src/android/widget/cts/AbsListView_LayoutParamsTest.java
    for root, dirs, files in os.walk("/home/gpoor/cts-source/cts/"):  # tests/tests/widget/src/android/widget/cts"):

        for file in files:
            if file.endswith('.java'):
                fullpath = '{}/{}'.format(root, file)
                with open(fullpath, "r") as text_file:
                    file_string = text_file.read()
                    for reference in reference_diction:
                        files_as_seperated_strings = collected_value.get(reference)
                        if files_as_seperated_strings:
                            path_set = set(files_as_seperated_strings.split(' '))
                        else:
                            path_set = set()
                        value_set = reference_diction[reference]
                        values = str(value_set).split(' ')
                        for value in values:
                            value = value.strip(' ').strip('.')
                            if len(value) > 2:
                                result = file_string.find(value)
                                if result > -1:
                                    count += 1
                                    if (count % 100) == 0:
                                        end_time_file_crawl = time.perf_counter()
                                        print(
                                            f'{count} time {end_time_file_crawl - start_time_file_crawl:0.4f}sec {reference} found {value} in  {fullpath}')
                                    path_set.add(fullpath)
                                    value_matched[value] = fullpath
                        if len(path_set) > 0:
                            collected_value[reference] = ' '.join(path_set)

    end_time_file_crawl = time.perf_counter()
    print(
        f'Final return {len(collected_value)}, {count} time {end_time_file_crawl - start_time_file_crawl:0.4f}  {collected_value}')
    return collected_value  # , value_matched


def read_table(file_name: str):
    table = []
    read_header: [str]
    keys_from_table: dict = dict()
    with open(file_name) as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            if line_count == 0:
                if row.index(default_header[0]) > -1:
                    print(f'Column names are {", ".join(row)}')
                    read_header = row
                    line_count += 1
                else:
                    raise Exception(
                        f' First row of file {csv_file} should contain CSV with header like {default_header} looking for <Section> not found in {row}')
            else:
                print(f'\t{row[0]} row 1 {row[1]}  row 2 {row[2]}.')
                table.append(row)
                table_index = line_count - 1
                # Section,section_id,req_id
                # section_value = table[table_index][read_header.index(default_header[0])]
                section_id_value = table[table_index][read_header.index(default_header[1])]
                req_id_value = table[table_index][read_header.index(default_header[2])]
                # class_def_value = table[table_index][read_header.index("class_def")]
                # method_value = table[table_index][read_header.index("method")]
                # module_value = table[table_index][read_header.index("module")]
                key_value = '{}/{}'.format(section_id_value.rstrip('.'), req_id_value)
                keys_from_table[key_value] = table_index
                line_count += 1
                print(f'Processed {line_count} lines {key_value} ')
            print(f'For table {line_count}')
        print("End for loop")
        return table, keys_from_table, read_header

    # find urls that may help find the tests for the requirement


def find_urls(text_to_scan_urls: str):
    find_url_re_str = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return " ".join(set(re.findall(find_url_re_str, text_to_scan_urls)))


# find likely java objects from a text block
def find_java_objects(text_to_scan_for_java_objects: str):
    java_objects = set()

    java_objects.update(cleanhtml(process_requirement_text(text_to_scan_for_java_objects)).split(' '))
    java_objects = sourcecrawlerreducer.SourceCrawlerReducer().remove_non_determinative_words(java_objects)
    java_methods_re_str = '(?:[a-zA-Z]\w+\( ?\w* ?\))'
    java_objects.update(re.findall(java_methods_re_str, text_to_scan_for_java_objects))

    java_object_re_str = '(?:[a-zA-Z]\w+\.)+[a-zA-Z_][a-zA-Z]+'
    java_objects.update(re.findall(java_object_re_str, text_to_scan_for_java_objects))

    java_defines_str = '[A-Z][A-Z0-9]{2,20}[_A-Z0-9]{0,40}'
    java_objects.update(re.findall(java_defines_str, text_to_scan_for_java_objects))
    java_objects.difference_update(
        {"MUST", "SHOULD", "API", 'source.android.com', 'NOT', 'SDK', 'MAY', 'AOSP', 'STRONGLY',
         'developer.android.com'})

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


def handle_java_files_data(key_str, keys_to_files_dict, table, table_row_index, files_to_test_cases: dict,
                           files_to_words, method_to_words, files_to_method_calls: dict, test_file_to_dependencies,
                           overwrite: bool = False):
    if keys_to_files_dict:
        filenames_str = keys_to_files_dict.get(key_str)
        found_methods = None
        file_name = None
        a_method = None
        if filenames_str:
            filenames = filenames_str.split(' ')
            if len(filenames) > 0:
                # TODO just handling one file for now! Needs to change.
                a_single_test_file_name = filenames[len(filenames) - 1]
                for file_name in filenames:
                    found_methods = files_to_method_calls.get(file_name)
                    if found_methods:
                        break
                if found_methods:
                    # A better single file name :)
                    a_single_test_file_name = file_name
                    for method in found_methods:
                        a_method = method

                table[table_row_index].append(a_single_test_file_name)
                # table[table_row_index].append(filenames_str)

                class_name_split_src = a_single_test_file_name.split('/src/')
                # Module
                if len(class_name_split_src) > 0:
                    test_case_split = str(class_name_split_src[0]).split('/cts/tests/')
                    if len(test_case_split) > 1:
                        project_root = str(test_case_split[1]).replace("/", ".")
                        test_case_name = files_to_test_cases.get(project_root)
                        if overwrite or (table[table_row_index][9] == ""):
                            table[table_row_index][9] = test_case_name
                if len(class_name_split_src) > 1:
                    class_name = str(class_name_split_src[1]).replace("/", ".").rstrip(".java")
                    if overwrite or (table[table_row_index][7] == ""):
                        table[table_row_index][7] = class_name
                        if overwrite or (table[table_row_index][7] == ""):
                            table[table_row_index][3] = "Test Available"
                if a_method:
                    if overwrite or (table[table_row_index][8] == ""):
                        table[table_row_index][8] = a_method


def write_sheet(write_row_for_output: (), file_name: str, table: [[str]], keys_to_find_and_write, keys_for_section_data,
                key_to_java_objects, key_to_urls):
    try:
        keys_to_files_dict = persist.read("storage/keys_to_files_dict.csv")
    except IOError:
        print("Could not open key to file map, recreating ")
        keys_to_files_dict: dict = find_test_files(key_to_java_objects)
        persist.write(keys_to_files_dict, "storage/keys_to_files_dict.csv")
    # Map file to TestCase

    # test_file_to_dependencies

    try:
        test_file_to_dependencies = persist.read("storage/test_file_to_dependencies.pickle")
    except IOError:
        print("Could not open android_studio_dependencies_for_cts, recreating ")
        test_file_to_dependencies = class_graph.ReadClassGraph().parse_dependency_file(
            'input/android_studio_dependencies_for_cts.txt')
        persist.write(test_file_to_dependencies, "storage/test_file_to_dependencies.pickle")

    files_to_words, method_to_words, files_to_method_calls, aggregate_bag = sourcecrawlerreducer.SourceCrawlerReducer().get_cached_crawler_data()

    files_to_test_cases = build_test_cases_module_dictionary('input/testcases-modules.txt')
    with open(file_name, 'w', newline='') as csv_output_file:
        table_row_index = 0
        keys_not_found: set = set()

        for temp_key in keys_to_find_and_write:
            key_str: str = temp_key
            key_str = key_str.rstrip(".").strip(' ')

            section_data = keys_for_section_data.get(key_str)
            write_row_for_output(key_str, key_to_java_objects, key_to_urls, keys_not_found,
                                 keys_to_files_dict, table_row_index, section_data, table,
                                 files_to_test_cases,
                                 files_to_words, method_to_words, files_to_method_calls, test_file_to_dependencies)
            table_row_index += 1

        table_writer = csv.writer(csv_output_file)
        table_writer.writerows(table)
        csv_output_file.close()
    return keys_not_found


default_header: [] = (
    ['Section', 'section_id', 'req_id', 'Test', 'Availability', 'Annotation?' ',''New Req for R?',
     'New CTS for R?', 'class_def', 'method', 'module',
     'Comment(internal) e.g. why a test is not possible ', 'Comment (external)',
     'New vs Updated(Q)', 'CTS Bug Id ', 'CDD Bug Id', 'CDD CL', 'Area', 'Shortened',
     'Test Level',
     '', 'external section_id', '', '', ''])


def write_new_data_line_to_table(key_str, key_to_java_objects, key_to_urls, keys_not_found,
                                 keys_to_files_dict, table_row_index, section_data: str, table: [[str]],
                                 files_to_test_cases,
                                 files_to_words, method_to_words, files_to_method_calls, test_file_to_dependencies):
    if len(table) <= table_row_index:
        table.append(['', '', '', '', '', '', '', '', '', '', '', ''])

    print(f"keys from  {table_row_index} [{key_str}]")
    key_str = key_str.rstrip(".").strip(' ')
    key_split = key_str.split('/')
    table[table_row_index][1] = key_split[0]

    table[table_row_index][3] = key_str
    section_data_cleaned = '"{}"'.format(section_data.replace("\n", " "))
    table[table_row_index].append(section_data_cleaned)

    if len(key_split) > 1:
        table[table_row_index][2] = key_split[1]
        table[table_row_index][4] = convert_version_to_number(key_split[0], key_split[1])
        table[table_row_index].append(key_to_urls.get(key_str))
        table[table_row_index].append(key_to_java_objects.get(key_str))
        handle_java_files_data(key_str, keys_to_files_dict, table, table_row_index, files_to_test_cases,
                               files_to_words, method_to_words, files_to_method_calls, test_file_to_dependencies)
    else:
        table[table_row_index][4] = convert_version_to_number(key_split[0])
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


def append_to_existing_data(key_str, key_to_java_objects, key_to_urls, keys_not_found, keys_to_files_dict,
                            table_row_index, section_data, table: [[str]], files_to_test_cases: dict,
                            files_to_words, method_to_words, files_to_method_calls, test_file_to_dependencies):
    if section_data:
        # Verify our index in the table we are augmenting corresponds to the key we are using to retrieve augmenting data
        table_key = f'{table[table_row_index][1]}/{table[table_row_index][2]}'
        if table_key != key_str:
            print(
                f'Error:  Table Key has a trailing "." Table key [{table_key}] key to append data [{key_str}] at line {table_row_index} remove and re test')
            # fix and test again.
            table[table_row_index][1] = str(table[table_row_index][1]).rstrip('.').strip(' ')
            table_key = f'{table[table_row_index][1]}/{table[table_row_index][2]}'
            if table_key != key_str:
                raise Exception(
                    f'Error Key mismatch! Table key [{table_key}] key to append data [{key_str}] at line {table_row_index}')
        table[table_row_index].append('{}'.format(section_data))
        print(f' Found[{key_str}] at table index {table_row_index} requirement_text=[{section_data}]')
    else:
        keys_not_found.add(key_str)
        print(f'NOT FOUND![{key_str}] at table index {table_row_index}   ')
        table[table_row_index].append(f'! ERROR {key_str}: Not found in data keys at table index {table_row_index} ')
        table[table_row_index].append(key_to_urls.get(key_str))
    table[table_row_index].append(key_to_java_objects.get(key_str))
    handle_java_files_data(key_str, keys_to_files_dict, table, table_row_index, files_to_test_cases,
                           files_to_words, method_to_words, files_to_method_calls, test_file_to_dependencies)

    table[table_row_index][4] = convert_version_to_number(table[table_row_index][1])
    table[table_row_index].append('Last augmented column')


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


def parse_cdd_html_to_requirements_table(table_file_name, cdd_html_file):
    key_to_full_requirement_text = dict()
    key_to_java_objects = dict()
    key_to_urls = dict()
    # Should do key_to_cdd_section = dict()
    keys_not_found: list = []
    table, keys_from_table, header = read_table(table_file_name)
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
        req_id_splits = re.split(composite_key_string_re, str(section))

        total_requirement_count = process_section(build_composite_key, req_id_re_str, cdd_section_id,
                                                  key_to_full_requirement_text,
                                                  key_to_java_objects, key_to_urls, req_id_splits,
                                                  section_id_count, total_requirement_count)
        full_key_string_for_re = '>(?:[0-9]{1,3}.)*[0-9]?[0-9]/' + req_id_re_str
        req_id_splits = re.split('(?={})'.format(full_key_string_for_re), section)
        total_requirement_count = process_section(find_full_key, full_key_string_for_re, cdd_section_id,
                                                  key_to_full_requirement_text,
                                                  key_to_java_objects, key_to_urls, req_id_splits,
                                                  section_id_count, total_requirement_count)
        section_id_count += 1
    return table, keys_from_table, key_to_full_requirement_text, key_to_java_objects, key_to_urls, keys_not_found, cdd_requirements_file_as_string


class AugmentSheetWithCDDInfo:

    def augment_table(self):
        table_to_augment, keys_from_table, key_to_full_requirement_text, key_to_java_objects, key_to_urls, keys_not_found, cdd_string = \
            parse_cdd_html_to_requirements_table('input/new_recs_remaining_todo.csv',
                                                 'input/Android 11 Compatibility Definition_no_section_13.html')

        # Write New Table
        created_table: [[str]] = []
        write_sheet(write_new_data_line_to_table, 'output/created_output.csv', created_table,
                    key_to_full_requirement_text, key_to_full_requirement_text, key_to_java_objects,
                    key_to_urls)

        # Write Augmented Table
        keys_not_found = write_sheet(append_to_existing_data, 'output/augmented_output.csv', table_to_augment,
                                     keys_from_table, key_to_full_requirement_text, key_to_java_objects,
                                     key_to_urls)

        found_count = len(keys_from_table)
        not_found_count = len(keys_not_found)
        print(f'Not {not_found_count} Found {found_count}  of {not_found_count + found_count}')


if __name__ == '__main__':
    start = time.perf_counter()
    AugmentSheetWithCDDInfo().augment_table()
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
