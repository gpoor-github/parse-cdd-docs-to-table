import os
import random
import time

from cdd_to_cts import class_graph, persist, static_data
from cdd_to_cts import helpers
from cdd_to_cts.data_sources_helper import convert_relative_filekey, get_file_dependencies, \
    parse_cdd_html_to_requirements, make_bags_of_word
from cdd_to_cts.helpers import convert_version_to_number, convert_version_to_number_from_full_key
from cdd_to_cts.helpers import make_files_to_string, build_test_cases_module_dictionary
from cdd_to_cts.static_data import CTS_SOURCE_PARENT, MANUAL_SEARCH_TERMS
from cdd_to_cts.static_data import CTS_SOURCE_ROOT, DATA_SOURCES_CSV_FROM_HTML_1st
from cdd_to_cts.table_ops import read_table_sect_and_req_key
from table_ops import write_table


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


def get_random_method_name(a_found_methods_string):
    a_method = None
    if a_found_methods_string:
        found_methods = a_found_methods_string.split(' ')
        if len(found_methods) > 0:
            a_method = found_methods[random.randrange(0, len(found_methods))]
    return a_method


class SourceCrawlerReducer(object):
    def __init__(self,
                 cdd_requirements_html_source: str = static_data.CDD_REQUIREMENTS_FROM_HTML_FILE.replace('../', ''),
                 global_table_input_file_build_from_html=DATA_SOURCES_CSV_FROM_HTML_1st,
                 cts_root_directory: str = CTS_SOURCE_ROOT,
                 do_search=False):

        self.global_to_data_sources_do_search = do_search
        self.test_files_to_aggregated_dependency_string = dict()

        self.__files_to_words, self.__method_to_words, self.__files_to_method_calls = self.get_cached_crawler_data(
            cts_root_directory)
        self.key_to_full_requirement_text, self.key_to_java_objects, self.key_to_urls, self.cdd_string, self.section_to_data = parse_cdd_html_to_requirements(
            cdd_requirements_html_source)
        self.create_full_table_from_cdd(self.key_to_full_requirement_text,self.key_to_full_requirement_text,global_table_input_file_build_from_html)

        self.global_input_table, self.global_input_table_keys_to_index, self.global_input_header, self.global_duplicate_rows = read_table_sect_and_req_key(
            global_table_input_file_build_from_html)

        self.__testfile_dependencies_to_words = get_file_dependencies()

        self.__test_files_to_strings = self.make_test_file_to_dependency_strings()
        #    class DataSources:
        self.files_to_test_cases = build_test_cases_module_dictionary(static_data.TEST_CASE_MODULES)

    files_to_words_storage = 'storage/files_to_words.pickle'
    method_to_words_storage = 'storage/method_to_words.pickle'
    files_to_method_calls_storage = 'storage/files_to_method_calls.pickle'
    testfile_dependencies_to_words_storage = 'storage/testfile_dependencies_to_words_storage.pickle'

    def __make_bags_of_testfile_dependency_word(self, files_to_words_inner: dict):
        # traverse root directory, and list directories as dirs and cts_files as cts_files

        test_files_to_aggregated_words: dict[str, set] = dict()
        # Have a test files and get all the words for it and it's dependencies
        for file in class_graph.get_cached_grep_of_at_test_files():
            file = str(file)
            aggregate_words_for_dependencies = set()
            a_files_to_word = files_to_words_inner.get(CTS_SOURCE_PARENT + file)
            aggregate_words_for_dependencies.update(a_files_to_word)
            dependencies: [str] = self.__testfile_dependencies_to_words.get(convert_relative_filekey(file))
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

    def make_test_file_to_dependency_strings(self, ):
        # traverse root directory, and list directories as dirs and cts_files as cts_files
        if len(self.test_files_to_aggregated_dependency_string) < 1:
            # Have a test files and get all the words for it and it's dependencies
            file_list = list()
            error_cnt = 0
            found_cnt = 0
            for test_file in class_graph.get_cached_grep_of_at_test_files():
                test_file = str(test_file)
                if test_file.endswith(".java"):
                    file_list.clear()
                    dependencies: [str] = self.get_testfile_dependency_word().get(convert_relative_filekey(test_file))
                    file_list.append(test_file)
                    if dependencies:
                        for dependency in dependencies:
                            file_list.append(dependency)
                    try:
                        self.test_files_to_aggregated_dependency_string[
                            test_file.replace(CTS_SOURCE_PARENT, '')] = make_files_to_string(file_list)
                        found_cnt += 1
                    except FileNotFoundError:
                        error_cnt += 1
                        print(f"Warning dependency {test_file} not found. error#={error_cnt} of {found_cnt}")

        return self.test_files_to_aggregated_dependency_string

    # This is handled on the re-act side for now .. only done if do_search is true.
    def handle_java_files_data(self, key_str):
        keys_to_files_dict = self.search_files_as_strings_for_words(key_str)
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
                    found_methods_string = class_graph.get_cached_grep_of_at_test_files().get(file_name_relative)
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
                        test_case_name = class_graph.search_for_test_case_name(a_single_test_file_name,
                                                                               self.files_to_test_cases)

                    if len(class_name_split_src) > 1:
                        class_name = str(class_name_split_src[1]).replace("/", ".").rstrip(".java")

            return a_single_test_file_name, test_case_name, a_method, class_name, a_found_methods_string, matched
        return None, None, None, None, None, None

    def search_files_for_words(self, key: str):
        java_objects = self.key_to_java_objects.get(key)
        count = 0
        # count, file_and_path, file_string, found_words_to_count:dict, matching_file_set_out:dict, key:str. value_set: set, start_time_file_crawl)
        matching_file_set_out = dict()
        if not java_objects:
            return matching_file_set_out
        word_to_count = dict()
        start_time_crawl = time.perf_counter()

        row = self.global_input_table[self.global_input_table_keys_to_index.get(key)]
        col_idx = list(self.global_input_header).index("manual_search_terms")
        if col_idx >= 0:
            if row[col_idx]:
                manual_search_terms = set(row[col_idx].split(' '))
                java_objects.update(manual_search_terms)
        for item in self.__files_to_words.items():
            words = item[1]
            if words:
                matching_file_set_out = diff_set_of_search_values_against_sets_of_words_from_files(count=count,
                                                                                                   file_and_path=item[
                                                                                                       0],
                                                                                                   word_set=words,
                                                                                                   found_words_to_count=word_to_count,
                                                                                                   matching_file_set_out=matching_file_set_out,
                                                                                                   key=key,
                                                                                                   search_terms=java_objects,
                                                                                                   start_time_file_crawl=start_time_crawl)
        return matching_file_set_out

    def search_files_as_strings_for_words(self, key: str):
        search_terms = self.key_to_java_objects.get(key)
        # count, file_and_path, file_string, found_words_to_count:dict, matching_file_set_out:dict, key:str. value_set: set, start_time_file_crawl)
        matching_file_set_out = dict()
        if search_terms:
            row = list()
            try:
                row = self.global_input_table[self.global_input_table_keys_to_index.get(key)]
            except Exception as err:
                helpers.raise_error(f"Exception [{key}] row not found in search_files_as_strings_for_word ", err)

            try:
                col_idx = list(self.global_input_header).index(MANUAL_SEARCH_TERMS)

                if col_idx >= 0:
                    if row[col_idx]:
                        manual_search_terms = set(row[col_idx].split(' '))
                        search_terms.update(manual_search_terms)
            except ValueError:
                print("warning no search manual search terms")
            pass
            for test_file in self.__test_files_to_strings:
                file_string = self.__test_files_to_strings.get(test_file)
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

    def get_cached_crawler_data(self, cts_root_directory=CTS_SOURCE_ROOT):
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
            self.__files_to_words, self.__method_to_words, self.__files_to_method_calls = make_bags_of_word(
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

    def create_populated_table(self, key_to_full_requirement_text:[str,str], keys_to_find_and_write:iter, header: []):
        table: [[str]] = []
        keys_to_table_index: dict[str, int] = dict()
        table_row_index = 0
        for temp_key in keys_to_find_and_write:
            key_str: str = temp_key
            key_str = key_str.rstrip(".").strip(' ')
            self.write_new_data_line_to_table(key_str, key_to_full_requirement_text, table,
                                              table_row_index, header)  # test_file_to_dependencies)
            keys_to_table_index[key_str] = table_row_index
            table_row_index += 1
        return table, keys_to_table_index

    # Section,section_id,req_id,Test Availability,Annotation? ,New Req for R?,New CTS for R?,class_def,method,module,
    # ['Section', SECTION_ID, 'req_id', 'Test Availability','class_def', 'method', 'module','full_key','requirement', 'key_as_number','search_terms','urls','file_name'])

    def write_new_data_line_to_table(self, key_str: str, keys_to_sections: dict, table: [[str]], table_row_index: int,
                                     header: [] = static_data.cdd_to_cts_app_header, logging=False):

        section_data = keys_to_sections.get(key_str)
        row: [str] = list(header)
        for i in range(len(row)):
            row[i] = ''
        if len(table) <= table_row_index:
            table.append(row)

        if logging: print(f"keys from  {table_row_index} [{key_str}]")
        key_str = key_str.rstrip(".").strip(' ')
        key_split = key_str.split('/')
        table[table_row_index][header.index('Section')] = self.section_to_data.get(
            key_split[0])

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
            if self.global_to_data_sources_do_search:
                a_single_test_file_name, test_case_name, a_method, class_name, a_found_methods_string, matched = self.handle_java_files_data(
                    key_str)

                table[table_row_index][header.index('module')] = test_case_name
                if a_single_test_file_name:
                    table[table_row_index][header.index('class_def')] = class_name
                    table[table_row_index][header.index(
                        'file_name')] = static_data.CTS_SOURCE_PARENT + a_single_test_file_name
                if a_method:
                    table[table_row_index][header.index('method')] = a_method
                    table[table_row_index][header.index('Test Availability')] = ""

                if matched:
                    table[table_row_index][header.index(static_data.MATCHED_FILES)] = a_single_test_file_name
                    table[table_row_index][header.index(static_data.MATCHED_TERMS)] = matched

                if a_found_methods_string:
                    table[table_row_index][header.index('methods_string')] = a_found_methods_string

        else:
            # This function handles having just a section_id
            table[table_row_index][header.index(static_data.KEY_AS_NUMBER)] = convert_version_to_number_from_full_key(
                key_split[0])
            print(f"Only a major key? {key_str}")

    # The new table ops merge table functions make this obsoleet
    # def update_table_table_from_cdd(self, created_table_file=static_data.WORKING_ROOT + "output/created_table.csv",
    #                                 update_table_file=static_data.WORKING_ROOT + "output/updated_table.csv",
    #                                 header: [] = static_data.cdd_to_cts_app_header):
    #     # Write New Table
    #     table_for_sheet, keys_to_table_indexes = self.create_populated_table(self.global_input_table_keys_to_index)
    #     write_table(created_table_file, table_for_sheet, header)
    #     # else:
    #     #     table_for_sheet, keys_to_table_indexes = create_populated_table(input_table, keys_from_input_table, input_header )  # Just a smaller table
    #     # Write Augmented Table
    #     updated_table, key_key1, key_key2 = update_table(self.global_input_table,
    #                                                      self.global_input_table_keys_to_index,
    #                                                      self.global_input_header, table_for_sheet,
    #                                                      keys_to_table_indexes, header,
    #                                                      static_data.merge_header)
    #     write_table(update_table_file, updated_table, self.global_input_header)
    #
    #     print(
    #         f'keys missing 1  {key_key1} keys missing 2 {key_key2}\nkeys1 missing  {len(key_key1)} keys2 missing {len(key_key2)} of {len(updated_table)}')

    def create_full_table_from_cdd(self,
                                   key_to_full_requirement_text:[str,str], keys_to_find_and_write,
                                   output_file: str,
                                   output_header: str = static_data.cdd_to_cts_app_header ):
        table_for_sheet, keys_to_table_indexes = self.create_populated_table( key_to_full_requirement_text,
                                                                              keys_to_find_and_write,
                                                                              output_header)
        print(f"CDD csv file to write to output is [{output_file}] output header is [{str(output_header)}]")

        write_table(output_file, table_for_sheet, output_header)


# Determines whether data_sources will try and search or not.

if __name__ == '__main__':
    start = time.perf_counter()
    cdd_11_html_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_download.html"
    cdd_11_table_generated_from_html_all = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_full_table_from_html.tsv"
    cdd_11_table_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_table_created.tsv" # So no filter
    cdd_12_html_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_download.html"
    cdd_12_table_generated_from_html_all = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_full_table_from_html.tsv"
    cdd_12_table_created = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_table_created.tsv"  # So no filter

    scr = SourceCrawlerReducer(
        cdd_requirements_html_source=cdd_12_html_file,
        global_table_input_file_build_from_html=cdd_12_table_generated_from_html_all,
        cts_root_directory=static_data.CTS_SOURCE_ROOT,
        do_search=False)
    scr.create_full_table_from_cdd(scr.key_to_full_requirement_text, scr.key_to_full_requirement_text,
                                   cdd_12_table_created,static_data.cdd_info_only_header)
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
