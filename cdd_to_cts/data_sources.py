import os
import random
import re
import time

from cdd_to_cts import class_graph, persist
from cdd_to_cts.data_sources_helper import convert_relative_filekey
from cdd_to_cts.helpers import  remove_non_determinative_words, bag_from_text, make_files_to_string
from cdd_to_cts.static_data import CTS_SOURCE_ROOT, CTS_SOURCE_PARENT


# find likely java objects from a text block
from cdd_to_cts.table_ops import read_table


def handle_java_files_data(key_str):
    from cdd_to_cts.init_data_sources import search_files_as_strings_for_words
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
                    test_case_key = str(class_name_split_src[0]).replace('cts/tests/', '')
                    if len(test_case_key) > 1:
                        project_root = str(test_case_key).replace("/", ".")
                        from cdd_to_cts.init_data_sources import files_to_test_cases
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

        method_call_re = re.compile(r'\w{3,40}(?=\(\w*\))(?!\s*?{)')
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
                            method_declare_body_splits = re.split(r'\s*public.+?\w+?(?=\(\w*?\))(?=.*?{)',
                                                                  test_method_split)
                            if len(method_declare_body_splits) > 1:
                                method_declare_body_split = method_declare_body_splits[1]
                                method_names = re.findall(r'\w{3,40}(?=\(:?\w*\))', test_method_split)

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
        for file in class_graph.get_cached_grep_of_at_test_files():
            file = str(file)
            aggregate_words_for_dependencies = set()
            a_files_to_word = files_to_words_inner.get(CTS_SOURCE_PARENT + file)
            aggregate_words_for_dependencies.update(a_files_to_word)
            from cdd_to_cts.init_data_sources import testfile_dependencies_to_words
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
        for test_file in class_graph.get_cached_grep_of_at_test_files():
            test_file = str(test_file)
            if test_file.endswith(".java"):
                file_list.clear()
                from cdd_to_cts.init_data_sources import testfile_dependencies_to_words
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

