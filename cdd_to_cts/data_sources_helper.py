#  Block to comment

from cdd_to_cts import class_graph, persist
from cdd_to_cts.static_data import TEST_FILES_TO_DEPENDENCIES_STORAGE
from class_graph import parse_dependency_file


#

# Section,section_id,req_id,Test Availability,Annotation? ,New Req for R?,New CTS for R?,class_def,method,module,
# ['Section', SECTION_ID, 'req_id', 'Test Availability','class_def', 'method', 'module','full_key','requirement', 'key_as_number','search_terms','urls','file_name'])


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
