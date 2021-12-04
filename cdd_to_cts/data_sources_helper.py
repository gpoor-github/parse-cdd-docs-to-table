#  Block to comment

import os
import re

import static_data
from cdd_to_cts import class_graph, persist, helpers
from cdd_to_cts.helpers import bag_from_text, remove_non_determinative_words, convert_version_to_number, \
    convert_version_to_number_from_full_key, filter_files_to_search
from cdd_to_cts.static_data import TEST_FILES_TO_DEPENDENCIES_STORAGE
from class_graph import parse_dependency_file


#
def create_populated_table(key_to_full_requirement_text:[str,str],keys_to_find_and_write:iter,  section_to_data:dict, header: []):
    table: [[str]] = []
    keys_to_table_index: dict[str, int] = dict()
    table_row_index = 0
    for temp_key in keys_to_find_and_write:
        key_str: str = temp_key
        key_str = key_str.rstrip(".").strip(' ')
        write_new_data_line_to_table(key_str, key_to_full_requirement_text, table, table_row_index, section_to_data, header)  # test_file_to_dependencies)
        keys_to_table_index[key_str] = table_row_index
        table_row_index += 1
    return table, keys_to_table_index

# Section,section_id,req_id,Test Availability,Annotation? ,New Req for R?,New CTS for R?,class_def,method,module,
# ['Section', SECTION_ID, 'req_id', 'Test Availability','class_def', 'method', 'module','full_key','requirement', 'key_as_number','search_terms','urls','file_name'])

def write_new_data_line_to_table( key_str: str, keys_to_sections: dict, table: [[str]], table_row_index: int,
                                 section_to_data: dict, header: [] = static_data.cdd_to_cts_app_header, search_func:()=None, logging=False):

    section_data = keys_to_sections.get(key_str)
    row: [str] = list(header)
    for i in range(len(row)):
        row[i] = ''
    if len(table) <= table_row_index:
        table.append(row)

    if logging: print(f"keys from  {table_row_index} [{key_str}]")
    key_str = key_str.rstrip(".").strip(' ')
    key_split = key_str.split('/')
    table[table_row_index][header.index('Section')] = section_to_data.get(key_str)

    table[table_row_index][header.index(static_data.SECTION_ID)] = key_split[0]

    table[table_row_index][header.index('full_key')] = key_str
    if section_data:
        section_data_cleaned = '"{}"'.format(section_data.replace("\n", " "))
        if len(section_data_cleaned) > 110000:
            print(f"Warning line to long truncating ")
            section_data_cleaned = section_data_cleaned[0:110000]
        table[table_row_index][header.index(static_data.REQUIREMENT)] = section_data_cleaned

    if len(key_split) > 1:
        table[table_row_index][header.index(static_data.REQ_ID)] = key_split[1]
        table[table_row_index][header.index(static_data.KEY_AS_NUMBER)] = convert_version_to_number(
            key_split[0], key_split[1])

        # This function takes a long time
        # This is handled in the React Side now
        if search_func:
            search_func(key_str)
    else:
        # This function handles having just a section_id
        table[table_row_index][header.index(static_data.KEY_AS_NUMBER)] = convert_version_to_number_from_full_key(
            key_split[0])
        if logging: print(f"Only a major key? {key_str}")

def create_full_table_from_cdd(
        key_to_full_requirement_text: [str, str], keys_to_find_and_write:iter,
        section_to_data: dict,
        output_file: str,
        output_header: str = static_data.cdd_to_cts_app_header):

    table_for_sheet, keys_to_table_indexes = create_populated_table(key_to_full_requirement_text,
                                                                    keys_to_find_and_write,
                                                                    section_to_data,
                                                                    output_header)
    print(f"CDD csv file to write to output is [{output_file}] output header is [{str(output_header)}]")

    from table_ops import write_table
    write_table(output_file, table_for_sheet, output_header)

def process_section_splits_md_and_html(record_key_method:(), key_string_for_re:str, section_id:str, key_to_full_requirement_text_param:dict[str, str],
                                       record_id_splits:[str], section_id_count:int, total_requirement_count:int, section_to_section_data:dict[str,str], section_data:str, logging=True):
    record_id_count = 0

    for record_id_split in record_id_splits:
        key = record_key_method(key_string_for_re, record_id_split, section_id)
        if key:
            record_id_count += 1
            total_requirement_count += 1
            key_to_full_requirement_text_param[key] = helpers.prepend_any_previous_value(record_id_split,
                                                                                         key_to_full_requirement_text_param.get(key))
            section_to_section_data[key] = section_data
            if logging: print(
                f'key [{key}] {key_string_for_re} value [{key_to_full_requirement_text_param.get(key)}] section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} ')

    return total_requirement_count


def get_file_dependencies():
    # if not testfile_dependencies_to_words:
    try:
        testfile_dependencies_to_words_local = parse_dependency_file()
        # testfile_dependencies_to_words_local = persist.read(TEST_FILES_TO_DEPENDENCIES_STORAGE)
    except IOError:
        print("Could not open android_studio_dependencies_for_cts, recreating ")
        testfile_dependencies_to_words_local = class_graph.parse_dependency_file()
        persist.write(testfile_dependencies_to_words_local, TEST_FILES_TO_DEPENDENCIES_STORAGE)
    return testfile_dependencies_to_words_local


def remove_ubiquitous_words_code(word_set_dictionary: [str, set]):
    test_suite_last = ""
    word_set_last = set()
    aggregate_set = set()
    for key in word_set_dictionary:
        test_suite = str(key)[0:str(key).find("/src")]
        if test_suite_last != test_suite:
            word_set_last = aggregate_set
            test_suite_last = test_suite
            aggregate_set.clear()
            aggregate_set.update(word_set_last)

        word_set = set(word_set_dictionary.get(key))
        filtered_word_set: set = word_set.difference(word_set_last)
        word_set_dictionary[key] = filtered_word_set

    return word_set_dictionary


def convert_relative_filekey(local_file: str):
    return '\"{}\"'.format(local_file.replace('cts/', '$PROJECT_DIR$/', 1))

#
# def make_bags_of_words_all(root_cts_source_directory):
#     # traverse root directory, and list directories as dirs and cts_files as cts_files
#
#     method_call_re = re.compile(r'\w{3,40}(?=\(\w*\))(?!\s*?{)')
#     files_to_words_local = dict()
#     method_to_words_local: dict = dict()
#     files_to_method_calls_local = dict()
#     for root, dirs, files in os.walk(root_cts_source_directory):
#         for file in files:
#             if filter_files_to_search(file):
#                 fullpath = '{}/{}'.format(root, file)
#                 with open(fullpath, "r") as text_file:
#                     file_string = text_file.read()
#                     text_file.close()
#
#                     bag = bag_from_text(file_string)
#                     files_to_words_local[fullpath] = remove_non_determinative_words(bag)
#                     # print(f'file {file} bag {bag}')
#
#                     # get the names we want to search for to see if they are declared in other cts_files
#                     files_to_method_calls_local[fullpath] = set(re.findall(method_call_re, file_string))
#
#                     test_method_splits = re.split("@Test", file_string)
#                     i = 1
#                     while i < len(test_method_splits):
#
#                         test_method_split = test_method_splits[i]
#                         method_declare_body_splits = re.split(r'\s*public.+?\w+?(?=\(\w*?\))(?=.*?{)',
#                                                               test_method_split)
#                         if len(method_declare_body_splits) > 1:
#                             method_declare_body_split = method_declare_body_splits[1]
#                             method_names = re.findall(r'\w{3,40}(?=\(:?\w*\))', test_method_split)
#
#                             method_bag = \
#                                 remove_non_determinative_words(set(method_declare_body_split.split(" ")))
#                             previous_value = method_to_words_local.get(fullpath)
#                             if previous_value:
#                                 method_to_words_local[fullpath] = method_names[0] + ":" + " ".join(
#                                     method_bag) + ' | ' + previous_value
#                             else:
#                                 method_to_words_local[fullpath] = method_names[0] + ":" + " ".join(method_bag)
#                         i += 1
#
#     return files_to_words_local, method_to_words_local, files_to_method_calls_local

# if __name__ == '__main__':
#     cdd_11_html_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_download.html"
#     cdd_11_table_generated_from_html_all = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_full_table_from_html.tsv"
#
#
#
#     key_to_full_requirement, key_to_java_objects, key_to_urls, cdd_as_string, section_to_section_data_test = \
#         parse_cdd_html_to_requirements(
#             cdd_html_file=cdd_11_html_file)
#     react.write_table_from_dictionary(key_to_full_requirement, cdd_11_table_generated_from_html_all)
