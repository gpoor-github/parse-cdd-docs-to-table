import os
import re
import time

import class_graph
import data_sources
import persist

CTS_SOURCE_ROOT = "/home/gpoor/cts-source/cts"

cdd_common_words = {'Requirement', 'Android', 'same', 'Types)', 'H:', 'The', 'implementations)', 'device',
                    'condition',
                    'Condition', 'any', 'unconditional;', '-', 'SR]', 'C:', 'Type', 'Tab:', 'implementation', '1',
                    'When', 'id=',
                    'assigned', ':', '2.', 'requirement', '(Requirements', 'consists', '(see', 'This', 'Each',
                    'ID', 'assigned.', 'Device', '1st', 'section', 'Watch', 'conditional;', 'A:', '<h4',
                    '(e.g.', 'type.', 'C-0-1).', 'T:', 'condition.', 'increments', 'defined', '0.', 'within',
                    'below:',
                    'applied', 'W:''', 'party', 'earlier', 'exempted', 'MUST', 'applications', 'requirement.',
                    'Devices', ';', 'support', 'document', 'level', 'through', 'logical', 'available',
                    'implementations', 'least', 'high', 'API', 'they:', 'If', 'launched', 'third', 'range'  "MUST",
                    "SHOULD",
                    "API", 'source.android.com', 'NOT', 'SDK', 'MAY', 'AOSP', 'STRONGLY',
                    'developer.android.com', 'Test', '@Test', 'app,data'}

common_methods = {'getFile', 'super', 'get', 'close', 'set', 'test', 'using', 'value', 'more' 'open', 'getType',
                  'getMessage', 'equals', 'not', 'find', 'search', 'length', 'size', 'getName', 'ToDo', 'from',
                  'String', 'HashMap'}

common_english_words = {'the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on',
                        'are', 'as', 'with', 'his', 'they', 'I', 'at', 'be', 'this', 'have', 'from', 'or', 'one',
                        'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when', 'your', 'can',
                        'said', 'there', 'use', 'an', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will',
                        'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
                        'would', 'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two', 'more', 'write', 'go',
                        'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been',
                        'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come',
                        'made', 'may', 'here'}

found_in_java_source = {
    'all', 'back', 'result', 'check', 'null', 'test', 'end', 'time', 'regular', 'able', 'start', 'Default',
    'times', 'timestamp', 'should', 'Build', 'Remote',
    'non', 'name', 'End', 'top', 'stop', 'class', 'Location', 'ID3', 'state', 'create', 'add', 'LOCATION_MODE',
    '0x00', 'present', 'sent', 'broadcast', 'Callback()',
    'Mode', 'mode', 'record', 'Method', 'app', 'previous', '800', 'call', 'connected', 'false', 'For', 'run',
    'batching', '-1000',
    'getName()', 'clear', 'per', 'under', 'Lock', 'disable', 'enable', 'content', 'size', 'actual', 'verify',
    'less', 'already', 'extend', 'text)', 'reflect',
    'signal', 'use', '2.0', 'variable', 'concurrent', 'lit', 'error', 'setting', 'expected', 'method', 'Report',
    'scanner', 'cases', 'change', 'device)', 'match', 'receive', 'param', 'manager', '180', 'only', 'class);',
    'Class', '200', 'bit', 'part', '(no', 'Using', 'action', 'devices)', '(generic', 'nor', 'before',
    'appropriate', 'it;', 'press', 'provide', 'equal', 'Open', 'true', 'except', 'right', 'Project', 'over',
    'Source', 'read', 'applicable', 'work', 'either', 'specific', 'See', 'language', 'Settings;', 'Package',
    'limitation', 'required', 'Pack', 'limitations', 'true;', 'context', 'file',
    'require', '(the', 'package', 'licenses', 'Unless', 'writing', '8000;', '(in', 'Filter;', 'soft', 'text;',
    'unit', 'New', 'copy', 'types', 'type', 'function', '1000', '100', 'used', '(10', 'determine', 'met',
    'annotation', 'fail', 'java.util.List', 'link',
    'first', 'functionalities', 'contains', 'contain', 'All', 'off', 'called', 'list', 'feature', 'whether',
    'implement', 'supported', 'devices', 'timeout', 'matched', 'com.android', 'tests',
    'Service;', 'correct', 'Profile;', 'support', 'Number', 'rect', 'parameters', 'parameter', 'matching',
    'states', 'profile)', 'position', 'begin', '10;', 'Level', 'allowed', 'more', 'Maximum', 'otherwise',
    'milliseconds', 'Access', 'seconds', 'form', 'hidden', 'invoke', 'array', 'platform', 'Such', 'ONLY', '(by',
    'class;', 'Simple', 'other', 'put', 'report', 'MAX', 'true);', '0x02', 'protect', 'known',
    'flags', 'level', "won't", 'unknown', 'cause', 'matches', 'turned', 'returned', 'lose', 'Key', 'behavior',
    'emulate', 'Can', 'Note', 'does', 'even', 'between', 'random', 'With', 'methods', 'must',
    'target', 'ID;', 'just', 'naming', 'characters', 'address', 'Generic', 'basic', 'original', 'reported',
    'running', 'complete', 'full', 'certain', 'based', 'away', 'want', 'once', 'real',
    'started', 'strong', 'buffer', 'range', 'next', 'base', 'far', 'completely', 'least', 'explicit', 'or;', 'declare',
    '(for', 'Are', 'source', 'preload', 'key', 'test('}

java_keywords = {'abstract', 'continue', 'for', 'new', 'switch', 'assert', '**', '*default', 'goto', '*', 'package',
                 'synchronized', 'boolean', 'do', 'if', 'private', 'this', 'break', 'double', 'implements',
                 'protected', 'throw', 'byte', 'else', 'import', 'public', 'throws', 'case', 'enum', '**', '**',
                 'instanceof', 'return', 'transient', 'catch', 'extends', 'int', 'short', 'try', 'char', 'final',
                 'interface', 'static', 'class', 'finally', 'long', 'strictfp', '**', 'volatile', 'const', '*',
                 'float', 'native', 'super', 'while', 'void', 'include', '#include'}

license_words = {
    "/** **/ ** Copyright 2020 The Android Open Source Project * * Licensed under the Apache License, Version 2.0 (the  License); "
    "* you may not use this file except in compliance with the License. * You may obtain a copy of the License at ** "
    "http://www.apache.org/licenses/LICENSE-2.0 * * Unless required by applicable law or agreed to in writing, software * distributed under the License is distributed on an AS IS"
    " BASIS, * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. * See the License for the specific language governing permissions and * limitations "
    "under the License.(C) \"AS IS\" */"}

all_words_to_skip: set = set().union(cdd_common_words).union(common_methods).union(common_english_words) \
    .union(found_in_java_source) \
    .union(java_keywords) \
    .union(license_words)


def remove_non_determinative_words(set_to_diff: set):
    return set_to_diff.difference(all_words_to_skip)


#
# def get_cached_keys_to_files(key_to_java_objects):
#     try:
#         keys_to_files_dict = persist.read("storage/keys_to_files_dict.csv")
#     except IOError:
#         print("Could not open key to file map, recreating ")
#         keys_to_files_dict: dict = __find_test_files(key_to_java_objects)
#         persist.write(keys_to_files_dict, "storage/keys_to_files_dict.csv")
#     return keys_to_files_dict


TEST_FILES_TO_DEPENDENCIES_STORAGE = 'storage/test_file_to_dependencies.pickle'


def get_file_dependencies():
    # traverse root directory, and list directories as dirs and cts_files as cts_files
    try:
        test_file_to_dependencies = persist.read(TEST_FILES_TO_DEPENDENCIES_STORAGE)
    except IOError:
        print("Could not open android_studio_dependencies_for_cts, recreating ")
        test_file_to_dependencies = class_graph.parse_dependency_file('input/android_studio_dependencies_for_cts.txt')
        persist.write(test_file_to_dependencies, TEST_FILES_TO_DEPENDENCIES_STORAGE)
    return test_file_to_dependencies


def read_files_to_string(file_list):
    start_time_file_crawl = time.perf_counter()

    files_to_strings: dict = dict()
    for file in file_list:
        if file.endswith('.java'):
            # fullpath = '{}/{}'.format(root, file)
            with open(file, "r") as text_file:
                file_string = text_file.read()
                files_to_strings[file] = file_string

    end_time_file_crawl = time.perf_counter()
    print(f'Took time {end_time_file_crawl - start_time_file_crawl:0.4f}sec ')

    return files_to_strings  # ,  sorted_words_keys


def search_string_with_set_of_values(count: int, file_and_path: str, word_set: set, found_words_to_count: dict,
                                     matching_file_set_out: dict, key: str,
                                     java_concat: str,
                                     start_time_file_crawl):

    value_set = remove_non_determinative_words(set(java_concat.split(' ')))
    keysplit = key.split('/')
    value_set.add(keysplit[0])
    value_set.add(keysplit[1])
    result = word_set.intersection(value_set)
    if len(result) > 0:
        count += 1
        if found_words_to_count.get(file_and_path):
            found_words_to_count[file_and_path ] = len(result) + found_words_to_count[file_and_path ]
        else:
            found_words_to_count[file_and_path] = result
        if (count % 100) == 0:
            end_time_file_crawl = time.perf_counter()
            print(
                f' {len(result) } {count} time {end_time_file_crawl - start_time_file_crawl:0.4f}sec {key}  path  {file_and_path}')
        matching_file_set_out[file_and_path] = count


    return matching_file_set_out


def search_files_for_words(key: str):
    keys_to_matched_files = dict
    test_files = data_sources.at_test_files_to_methods
    java_objects = data_sources.key_to_java_objects.get(key)
    count = 0
    # count, file_and_path, file_string, found_words_to_count:dict, matching_file_set_out:dict, key:str. value_set: set, start_time_file_crawl)
    start_time_crawl = time.perf_counter()
    matching_file_set_out = dict()
    word_to_count = dict()
    for test_file in test_files:
        # words =  ftw.get(test_file)
        words = data_sources.files_to_words.get("/home/gpoor/cts-source/" + test_file)
        if words:
            matching_file_set_out = search_string_with_set_of_values(count=count, file_and_path=test_file,
                                                                     word_set=words,
                                                                     found_words_to_count=word_to_count,
                                                                     matching_file_set_out=matching_file_set_out,
                                                                     key=key,
                                                                     java_concat=java_objects,
                                                                     start_time_file_crawl=start_time_crawl)
    return matching_file_set_out


class SourceCrawlerReducer:
    files_to_words_storage = 'storage/files_to_words.pickle'
    method_to_words_storage = 'storage/method_to_words.pickle'
    files_to_method_calls_storage = 'storage/files_to_method_calls.pickle'
    aggregate_bag_storage = 'storage/aggregate_bag.pickle'

    __files_to_words: dict = dict()
    __method_to_words: dict = dict()
    __files_to_method_calls: dict = dict()
    __aggregate_bag: dict = dict()

    def clear_cached_crawler_data(self):
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
            os.remove(self.aggregate_bag_storage)
        except IOError:
            pass

    def get_cached_crawler_data(self, cts_root_directory: str = CTS_SOURCE_ROOT):
        try:
            self.__files_to_words = persist.readp(self.files_to_words_storage)
            self.__method_to_words = persist.readp(self.method_to_words_storage)
            self.__files_to_method_calls = persist.readp(self.files_to_method_calls_storage)
            self.__aggregate_bag = persist.readp(self.aggregate_bag_storage)
            print(
                f"Returned cached value from  files_to_words {self.files_to_words_storage} , method_to_words {self.method_to_words_storage}, "
                f"files_to_method_calls {self.files_to_method_calls_storage}, aggregate_bag {self.aggregate_bag_storage} ")
        except IOError:
            print(
                f" Crawling {cts_root_directory}: Could not open files_to_words, method_to_words, files_to_method_calls, aggregate_bag , recreating ")
            self.__files_to_words, self.__method_to_words, self.__files_to_method_calls = self.__make_bags_of_word(
                cts_root_directory)
            persist.writep(self.__files_to_words, self.files_to_words_storage)
            persist.writep(self.__method_to_words, self.method_to_words_storage)
            persist.writep(self.__files_to_method_calls, self.files_to_method_calls_storage)
            persist.writep(self.__aggregate_bag, self.aggregate_bag_storage)
        return self.__files_to_words, self.__method_to_words, self.__files_to_method_calls

    @staticmethod
    def bag_from_text(text: str):
        file_string = re.sub("\s\s+", " ", text)
        split = file_string.split(" ")
        return set(split)

    @staticmethod
    def __make_bags_of_word(root_cts_source_directory):
        # traverse root directory, and list directories as dirs and cts_files as cts_files

        method_call_re = re.compile('\w{3,40}(?=\(\w*\))(?!\s*?\{)')
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

                        file_string = re.sub("\s\s+", " ", file_string)
                        # cts_files to words
                        split = file_string.split(" ")
                        bag = remove_non_determinative_words(set(split))
                        files_to_words_local[fullpath] = bag
                        # print(f'file {file} bag {bag}')

                        # get the names we want to search for to see if they are declared in other cts_files
                        files_to_method_calls_local[fullpath] = remove_non_determinative_words(
                            set(re.findall(method_call_re, file_string)))

                        test_method_splits = re.split("@Test", file_string)
                        i = 1
                        while i < len(test_method_splits):

                            test_method_split = test_method_splits[i]
                            method_declare_body_splits = re.split('\s*public.+?\w+?(?=\(\w*?\))(?=.*?\{)',
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


if __name__ == '__main__':
    start = time.perf_counter()
    scr = SourceCrawlerReducer()
    scr.clear_cached_crawler_data()
    files_to_words, method_to_words, files_to_method_call = \
        scr.get_cached_crawler_data('/home/gpoor/cts-source')
    print(f"\n\nfiles_to_words  [{files_to_words}] \nsize {len(files_to_words)}")
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
