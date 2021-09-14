import os
import random
import re
import time

import class_graph
import persist
from static_data_holder import CTS_SOURCE_PARENT, all_words_to_skip, REQUIREMENTS_FROM_HTML_FILE, \
    TEST_FILES_TO_DEPENDENCIES_STORAGE, CTS_SOURCE_ROOT
from table_ops import read_table


def remove_non_determinative_words(set_to_diff: set):
    return set_to_diff.difference(all_words_to_skip)


def find_urls(text_to_scan_urls: str):
    find_url_re_str = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return " ".join(set(re.findall(find_url_re_str, text_to_scan_urls)))


# find likely java objects from a text block
def find_java_objects(text_to_scan_for_java_objects: str) -> set:
    java_objects = set()

    #  java_objects.update(cleanhtml(process_requirement_text(text_to_scan_for_java_objects)).split(' '))
    java_methods_re_str = '(?:[a-zA-Z]\w+\( ?\w* ?\))'
    java_objects.update(re.findall(java_methods_re_str, text_to_scan_for_java_objects))

    java_object_re_str = '(?:[a-zA-Z]\w+\.)+[a-zA-Z_][a-zA-Z]+'
    java_objects.update(re.findall(java_object_re_str, text_to_scan_for_java_objects))

    java_defines_str = '[A-Z][A-Z0-9]{2,20}[_A-Z0-9]{0,40}'
    java_objects.update(re.findall(java_defines_str, text_to_scan_for_java_objects))

    java_objects = remove_non_determinative_words(java_objects)
    java_objects.discard(None)
    return java_objects


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
    keys_to_files_dict = search_files_as_strings_for_words(key_str)
    # keys_to_files_dict1 = sorted(keys_to_files_dict.items(), key=lambda x: x[1], reverse=True)
    a_single_test_file_name: str = ""
    test_case_name: str = ""
    class_name: str = ""
    matched: set = set()

    if keys_to_files_dict:
        # filenames_str = keys_to_files_dict.get(key_str)
        # found_methods = None
        a_method = None
        a_found_methods_string = None
        max_matches = -1
        if keys_to_files_dict:
            # TODO just handling one file for now! Needs to change.
            for file_name in keys_to_files_dict:
                file_name_relative = str(file_name).replace(CTS_SOURCE_PARENT, "")
                a_single_test_file_name = file_name_relative
                found_methods_string = at_test_files_to_methods.get(file_name_relative)
                a_method_candidate = get_random_method_name(found_methods_string)
                if a_method_candidate:
                    matched = keys_to_files_dict.get(file_name)
                    current_matches = len(matched)
                    if current_matches >= max_matches:
                        a_single_test_file_name = file_name_relative
                        a_method = a_method_candidate
                        max_matches = current_matches

                class_name_split_src = a_single_test_file_name.split('/src/')
                # Module
                if len(class_name_split_src) > 0:
                    test_case_key = str(class_name_split_src[0]).replace('cts/tests/', '')
                    if len(test_case_key) > 1:
                        project_root = str(test_case_key).replace("/", ".")
                        test_case_name = files_to_test_cases.get(project_root)

                if len(class_name_split_src) > 1:
                    class_name = str(class_name_split_src[1]).replace("/", ".").rstrip(".java")

        return a_single_test_file_name, test_case_name, a_method, class_name, a_found_methods_string, matched
    return None, None, None, None, None, None


def get_random_method_name(a_found_methods_string):
    a_method = None
    if a_found_methods_string:
        found_methods = a_found_methods_string.split(' ')
        if len(found_methods) > 0:
            a_method = found_methods[random.randrange(0, len(found_methods))]
    return a_method


def parse_cdd_html_to_requirements(cdd_html_file=REQUIREMENTS_FROM_HTML_FILE):
    key_to_full_requirement_text_local = dict()
    key_to_java_objects_local = dict()
    key_to_urls_local = dict()
    section_to_section_data = dict()
    # Should do key_to_cdd_section = dict()
    # keys_not_found: list = []
    total_requirement_count = 0
    with open(cdd_html_file, "r") as text_file:
        cdd_requirements_file_as_string = text_file.read()
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
        section_to_section_data[cdd_section_id] = str(cdd_section_id_search_results[0]).replace("\"", "")
        if '13' == cdd_section_id:
            # section 13 is "Contact us" and has characters that cause issues at lest for git
            print(f"Warning skipping section 13 {section}")
            continue
        key_to_full_requirement_text_local[cdd_section_id] = process_requirement_text(section, None)
        composite_key_string_re = "\s*(?:<li>)?\["
        req_id_re_str = '(?:Tab|[ACHTW])-[0-9][0-9]?-[0-9][0-9]?'
        full_key_string_for_re = '>(?:[0-9]{1,3}.)*[0-9]?[0-9]/' + req_id_re_str
        req_id_splits = re.split('(?={})'.format(full_key_string_for_re), section)
        total_requirement_count = process_section(find_full_key, full_key_string_for_re, cdd_section_id,
                                                  key_to_full_requirement_text_local, req_id_splits,
                                                  section_id_count, total_requirement_count)
        # Only build a key if you can't find any...
        if len(req_id_splits) < 2:
            req_id_splits = re.split(composite_key_string_re, str(section))

            total_requirement_count = process_section(build_composite_key, req_id_re_str, cdd_section_id,
                                                      key_to_full_requirement_text_local, req_id_splits,
                                                      section_id_count, total_requirement_count)

        section_id_count += 1
    for key in key_to_full_requirement_text_local:
        requirement_text = key_to_full_requirement_text_local.get(key)
        key_to_urls_local[key] = find_urls(requirement_text)
        key_split = key.split('/')

        java_objects_temp = find_java_objects(requirement_text)
        java_objects_temp.add(key_split[0])
        if len(key_split) > 1:
            java_objects_temp.add(key_split[1])
        key_to_java_objects_local[key] = java_objects_temp

    return key_to_full_requirement_text_local, key_to_java_objects_local, key_to_urls_local, cdd_requirements_file_as_string, section_to_section_data


def process_section(record_key_method, key_string_for_re, section_id, key_to_full_requirement_text_param,
                    record_id_splits, section_id_count, total_requirement_count):
    record_id_count = 0

    for record_id_split in record_id_splits:
        key = record_key_method(key_string_for_re, record_id_split, section_id)
        if key:
            record_id_split = clean_html_anchors(record_id_split)
            record_id_count += 1
            total_requirement_count += 1
            print(
                f'key [{key}] {key_string_for_re} value [{key_to_full_requirement_text_param.get(key)}] section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} ')
            key_to_full_requirement_text_param[key] = process_requirement_text(record_id_split,
                                                                               key_to_full_requirement_text_param.get(
                                                                                   key))
    return total_requirement_count


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


def read_file_to_string(file):
    with open(CTS_SOURCE_PARENT + file, "r") as text_file:
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


def get_file_dependencies():
    # if not testfile_dependencies_to_words:
    try:
        testfile_dependencies_to_words_local = persist.read(TEST_FILES_TO_DEPENDENCIES_STORAGE)
    except IOError:
        print("Could not open android_studio_dependencies_for_cts, recreating ")
        testfile_dependencies_to_words_local = class_graph.parse_dependency_file()
        persist.write(testfile_dependencies_to_words_local, TEST_FILES_TO_DEPENDENCIES_STORAGE)
    return testfile_dependencies_to_words_local


def diff_set_of_search_values_against_sets_of_words_from_files(count: int, file_and_path: str, word_set: set,
                                                               found_words_to_count: dict,
                                                               matching_file_set_out: dict, key: str,
                                                               search_terms: set,
                                                               start_time_file_crawl):
    if search_terms:
        result = word_set.intersection(search_terms)

        if len(result) > 0:
            count += 1
            if found_words_to_count.get(file_and_path):
                found_words_to_count[file_and_path] = len(result) + int(found_words_to_count[file_and_path])
            else:
                found_words_to_count[file_and_path] = len(result) + 5
            if (count % 100) == 0:
                end_time_file_crawl = time.perf_counter()
                print(
                    f' {len(result)} {count} time {end_time_file_crawl - start_time_file_crawl:0.4f}sec {key}  path  {file_and_path}')
            if not matching_file_set_out.get(file_and_path):
                matching_file_set_out[file_and_path] = result
            else:
                matching_file_set_out[key].update(result)

    else:
        print("warning no search terms ")
    return matching_file_set_out


def search_files_as_strings_for_words(key: str):
    search_terms = key_to_java_objects.get(key)
    # count, file_and_path, file_string, found_words_to_count:dict, matching_file_set_out:dict, key:str. value_set: set, start_time_file_crawl)
    matching_file_set_out = dict()
    if not search_terms:
        return matching_file_set_out

    row = global_input_table[global_input_table_keys_to_index.get(key)]
    try:
        col_idx = list(global_input_header).index("manual_search_terms")

        if col_idx >= 0:
            if row[col_idx]:
                manual_search_terms = set(row[col_idx].split(' '))
                search_terms.update(manual_search_terms)
    except ValueError:
        print("warning no search manual search terms")
    pass

    for test_file in test_files_to_strings:
        file_string = test_files_to_strings.get(test_file)
        match_count = 0
        match_set = set()
        if search_terms:
            for search_term in search_terms:
                this_terms_match_count = file_string.count(search_term)
                if this_terms_match_count > 0:
                    match_set.add(search_term)
                    match_count += this_terms_match_count
            if len(match_set) > 0:
                matching_file_set_out[test_file] = matching_file_set_out
    return matching_file_set_out


def search_files_for_words(key: str):
    java_objects = key_to_java_objects.get(key)
    count = 0
    # count, file_and_path, file_string, found_words_to_count:dict, matching_file_set_out:dict, key:str. value_set: set, start_time_file_crawl)
    matching_file_set_out = dict()
    if not java_objects:
        return matching_file_set_out
    word_to_count = dict()
    start_time_crawl = time.perf_counter()

    row = global_input_table[global_input_table_keys_to_index.get(key)]
    col_idx = list(global_input_header).index("manual_search_terms")
    if col_idx >= 0:
        if row[col_idx]:
            manual_search_terms = set(row[col_idx].split(' '))
            java_objects.update(manual_search_terms)
    for item in files_to_words.items():
        words = item[1]
        if words:
            matching_file_set_out = diff_set_of_search_values_against_sets_of_words_from_files(count=count,
                                                                                               file_and_path=item[0],
                                                                                               word_set=words,
                                                                                               found_words_to_count=word_to_count,
                                                                                               matching_file_set_out=matching_file_set_out,
                                                                                               key=key,
                                                                                               search_terms=java_objects,
                                                                                               start_time_file_crawl=start_time_crawl)
    return matching_file_set_out


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


class SourceCrawlerReducer:
    files_to_words_storage = 'storage/files_to_words.pickle'
    method_to_words_storage = 'storage/method_to_words.pickle'
    files_to_method_calls_storage = 'storage/files_to_method_calls.pickle'
    testfile_dependencies_to_words_storage = 'storage/testfile_dependencies_to_words_storage.pickle'

    __files_to_words: dict = None
    __method_to_words: dict = None
    __files_to_method_calls: dict = None
    __testfile_dependencies_to_words: dict = None

    def clear_cached_crawler_data(self):

        __files_to_words = None
        __method_to_words = None
        __files_to_method_calls = None
        try:
            os.remove(self.files_to_words_storage)
        except IOError:
            pass
        try:
            os.remove(self.method_to_words_storage)
        except IOError:
            pass
        try:
            os.remove(self.files_to_method_calls_storage)
        except IOError:
            pass

    def get_cached_crawler_data(self, cts_root_directory: str = CTS_SOURCE_ROOT):
        if not self.__files_to_words or self.__method_to_words or self.__files_to_method_calls:
            try:
                self.__files_to_words = persist.readp(self.files_to_words_storage)
                self.__method_to_words = persist.readp(self.method_to_words_storage)
                self.__files_to_method_calls = persist.readp(self.files_to_method_calls_storage)
                print(
                    f"Returned cached value from  files_to_words {self.files_to_words_storage} , method_to_words {self.method_to_words_storage}, "
                    f"files_to_method_calls {self.files_to_method_calls_storage} ")
            except IOError:
                print(
                    f" Crawling {cts_root_directory}: Could not open files_to_words, method_to_words, files_to_method_calls, aggregate_bag , recreating ")
                self.__files_to_words, self.__method_to_words, self.__files_to_method_calls = self.__make_bags_of_word(
                    cts_root_directory)
                persist.writep(self.__files_to_words, self.files_to_words_storage)
                persist.writep(self.__method_to_words, self.method_to_words_storage)
                persist.writep(self.__files_to_method_calls, self.files_to_method_calls_storage)
        return self.__files_to_words, self.__method_to_words, self.__files_to_method_calls

    def get_testfile_dependency_word(self):
        if not self.__testfile_dependencies_to_words:
            try:
                self.__testfile_dependencies_to_words = persist.readp(self.testfile_dependencies_to_words_storage)
            except IOError:
                print(
                    f" : Could not open __testfile_dependencies_to_words, recreating ")
                files_to_words_local, dummy1, dummy2 = self.get_cached_crawler_data()
                self.__testfile_dependencies_to_words = self.__make_bags_of_testfile_dependency_word(
                    files_to_words_local)
                persist.writep(self.__testfile_dependencies_to_words, self.testfile_dependencies_to_words_storage)
        return self.__testfile_dependencies_to_words

    @staticmethod
    def __make_bags_of_word(root_cts_source_directory):
        # traverse root directory, and list directories as dirs and cts_files as cts_files

        method_call_re = re.compile('\w{3,40}(?=\(\w*\))(?!\s*?{)')
        files_to_words_local = dict()
        method_to_words_local: dict = dict()
        files_to_method_calls_local = dict()
        for root, dirs, files in os.walk(root_cts_source_directory):
            for file in files:
                if file.endswith('.java'):
                    fullpath = '{}/{}'.format(root, file)
                    with open(fullpath, "r") as text_file:
                        file_string = text_file.read()
                        text_file.close()

                        bag = bag_from_text(file_string)
                        files_to_words_local[fullpath] = remove_non_determinative_words(bag)
                        # print(f'file {file} bag {bag}')

                        # get the names we want to search for to see if they are declared in other cts_files
                        files_to_method_calls_local[fullpath] = set(re.findall(method_call_re, file_string))

                        test_method_splits = re.split("@Test", file_string)
                        i = 1
                        while i < len(test_method_splits):

                            test_method_split = test_method_splits[i]
                            method_declare_body_splits = re.split('\s*public.+?\w+?(?=\(\w*?\))(?=.*?{)',
                                                                  test_method_split)
                            if len(method_declare_body_splits) > 1:
                                method_declare_body_split = method_declare_body_splits[1]
                                method_names = re.findall('\w{3,40}(?=\(:?\w*\))', test_method_split)

                                method_bag = \
                                    remove_non_determinative_words(set(method_declare_body_split.split(" ")))
                                previous_value = method_to_words_local.get(fullpath)
                                if previous_value:
                                    method_to_words_local[fullpath] = method_names[0] + ":" + " ".join(
                                        method_bag) + ' | ' + previous_value
                                else:
                                    method_to_words_local[fullpath] = method_names[0] + ":" + " ".join(method_bag)
                            i += 1

        return files_to_words_local, method_to_words_local, files_to_method_calls_local

    @staticmethod
    def __make_bags_of_testfile_dependency_word(files_to_words_inner: dict):
        # traverse root directory, and list directories as dirs and cts_files as cts_files

        test_files_to_aggregated_words: dict[str, set] = dict()
        # Have a test files and get all the words for it and it's dependencies
        for file in at_test_files_to_methods:
            file = str(file)
            aggregate_words_for_dependencies = set()
            a_files_to_word = files_to_words_inner.get(CTS_SOURCE_PARENT + file)
            aggregate_words_for_dependencies.update(a_files_to_word)
            dependencies: [str] = testfile_dependencies_to_words.get(convert_relative_filekey(file))
            if dependencies:
                for i in range(len(dependencies)):
                    dependency: str = dependencies[i]
                    if dependency:
                        a_files_to_word = files_to_words_inner.get(
                            dependency.strip('\"').replace('$PROJECT_DIR$', CTS_SOURCE_ROOT))
                        if a_files_to_word:
                            aggregate_words_for_dependencies.update(a_files_to_word)
                test_files_to_aggregated_words[file] = aggregate_words_for_dependencies

        return test_files_to_aggregated_words

    @staticmethod
    def make_test_file_to_dependency_strings():
        # traverse root directory, and list directories as dirs and cts_files as cts_files

        test_files_to_aggregated_dependency_string: dict[str, str] = dict()
        # Have a test files and get all the words for it and it's dependencies
        file_list = list()
        error_cnt = 0
        found_cnt = 0
        for test_file in at_test_files_to_methods:
            test_file = str(test_file)
            if test_file.endswith(".java"):
                file_list.clear()
                dependencies: [str] = testfile_dependencies_to_words.get(convert_relative_filekey(test_file))
                file_list.append(test_file)
                if dependencies:
                    for i in range(len(dependencies)):
                        dependency: str = dependencies[i]
                        file_list.append(dependency)
                try:
                    test_files_to_aggregated_dependency_string[
                        test_file.replace(CTS_SOURCE_PARENT, '')] = make_files_to_string(file_list)
                    found_cnt += 1
                except FileNotFoundError:
                    error_cnt += 1
                    print(f"Warning dependency {test_file} not found. error#={error_cnt} of {found_cnt}")
                    pass
        print(
            f"Dependencies found={len(test_files_to_aggregated_dependency_string)} not found. error#={error_cnt} of {found_cnt}")

        return test_files_to_aggregated_dependency_string


def convert_relative_filekey(local_file: str):
    return '\"{}\"'.format(local_file.replace('cts/', '$PROJECT_DIR$/', 1))


# global_input_file_name = "input/2021-09-11-CDD-11-Sachiyo-Aug-4-restore.csv"
global_input_file_name = "input/new_recs_remaining_todo.csv"

global_input_table, global_input_table_keys_to_index, global_input_header, global_duplicate_rows = read_table(
    global_input_file_name)
key_to_full_requirement_text, key_to_java_objects, key_to_urls, cdd_string, section_to_data = parse_cdd_html_to_requirements()

#    class DataSources:
files_to_test_cases = build_test_cases_module_dictionary('input/testcases-modules.txt')
at_test_files_to_methods = class_graph.get_cached_grep_of_at_test_files()

files_to_words, method_to_words, files_to_method_calls = SourceCrawlerReducer().get_cached_crawler_data()
testfile_dependencies_to_words = get_file_dependencies()

test_files_to_strings = SourceCrawlerReducer.make_test_file_to_dependency_strings()

if __name__ == '__main__':
    start = time.perf_counter()
    scr = SourceCrawlerReducer()
    #  scr.clear_cached_crawler_data()
    files_to_words, method_to_words, files_to_method_call = \
        scr.get_cached_crawler_data(CTS_SOURCE_PARENT)
    # remove_ubiquitous_words_code(files_to_words)
    test_files_to_strings = scr.make_test_file_to_dependency_strings()

    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
