import os
import re
import time

import persist


class SourceCrawlerReducer:
    common_english_words = {'the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on',
                            'are', 'as', 'with', 'his', 'they', 'I', 'at', 'be', 'this', 'have', 'from', 'or', 'one',
                            'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when', 'your', 'can',
                            'said', 'there', 'use', 'an', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will',
                            'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
                            'would', 'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two', 'more', 'write', 'go',
                            'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been',
                            'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come',
                            'made', 'may'}

    java_keywords = {'abstract', 'continue', 'for', 'new', 'switch', 'assert', '**', '*default', 'goto', '*', 'package',
                     'synchronized', 'boolean', 'do', 'if', 'private', 'this', 'break', 'double', 'implements',
                     'protected', 'throw', 'byte', 'else', 'import', 'public', 'throws', 'case', 'enum', '**', '**',
                     'instanceof', 'return', 'transient', 'catch', 'extends', 'int', 'short', 'try', 'char', 'final',
                     'interface', 'static', 'class', 'finally', 'long', 'strictfp', '**', 'volatile', 'const', '*',
                     'float', 'native', 'super', 'while', 'void'}
    common_methods = {'getFile', 'super', 'get', 'close', 'set', 'test', 'open', 'getType', 'getMessage', 'equals',
                      'not', 'find', 'search', 'length', 'size', 'getName', 'ToDo', 'from', 'String', 'HashMap'}
    license_words = {
        "/** **/ ** Copyright 2020 The Android Open Source Project * * Licensed under the Apache License, Version 2.0 (the  License); "
        "* you may not use this file except in compliance with the License. * You may obtain a copy of the License at ** "
        "http://www.apache.org/licenses/LICENSE-2.0 * * Unless required by applicable law or agreed to in writing, software * distributed under the License is distributed on an AS IS"
        " BASIS, * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. * See the License for the specific language governing permissions and * limitations "
        "under the License.(C) \"AS IS\" */"}
    files_to_words_storage = 'storage/files_to_words.pickle'
    method_to_words_storage = 'storage/method_to_words.pickle'
    files_to_method_calls_storage = 'storage/files_to_method_calls.pickle'
    aggregate_bag_storage = 'storage/aggregate_bag.pickle'

    __files_to_words: dict = dict()
    __method_to_words: dict = dict()
    __files_to_method_calls: dict = dict()
    __aggregate_bag:dict = dict()

    def clear_cached_crawler_data(self):
        try:
            os.remove(self.files_to_words_storage)
        except:
            pass
        try:
            os.remove(self.method_to_words_storage)
        except:
            pass
        try:
            os.remove(self.files_to_method_calls_storage)
            os.remove(self.aggregate_bag_storage)
        except:
            pass

    def get_cached_crawler_data(self, cts_root_directory: str ='/home/gpoor/cts-source'):
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
            self.__files_to_words, self.__method_to_words, self.__files_to_method_calls, self.__aggregate_bag = self.__make_bags_of_word(
                cts_root_directory)
            persist.writep(self.__files_to_words, self.files_to_words_storage)
            persist.writep(self.__method_to_words, self.method_to_words_storage)
            persist.writep(self.__files_to_method_calls, self.files_to_method_calls_storage)
            persist.writep(self.__aggregate_bag, self.aggregate_bag_storage)
        return self.__files_to_words, self.__method_to_words, self.__files_to_method_calls, self.__aggregate_bag

    def bag_from_text(self, text: str):
        file_string = re.sub("\s\s+", " ", text)
        split = file_string.split(" ")
        return set(split)

    def __make_bags_of_word(self, root_cts_source_directory):
        # traverse root directory, and list directories as dirs and files as files

        method_call_re = re.compile('\w{3,40}(?=\(\w*\))(?!\s*?\{)')
        files_to_words = dict()
        method_to_words = dict()
        files_to_method_calls = dict()
        aggregate_bag = dict()
        for root, dirs, files in os.walk(root_cts_source_directory):
            for file in files:
                if file.endswith('.java'):
                    fullpath = '{}/{}'.format(root, file)
                    with open(fullpath, "r") as text_file:
                        file_string = text_file.read()
                        text_file.close()

                        file_string = re.sub("\s\s+", " ", file_string)
                        # files to words
                        split = file_string.split(" ")
                        bag = self.remove_non_determinative_words(set(split))
                        files_to_words[fullpath] = bag
                        # print(f'file {file} bag {bag}')
                        #aggregate_bag.update(bag)

                        # get the names we want to search for to see if they are declared in other files
                        files_to_method_calls[fullpath] = self.remove_non_determinative_words(
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
                                    self.remove_non_determinative_words(set(method_declare_body_split.split(" ")))
                                previous_value = method_to_words.get(fullpath)
                                if previous_value:
                                    method_to_words[fullpath] = method_names[0] + ":" + " ".join(
                                        method_bag) + ' | ' + previous_value
                                else:
                                    method_to_words[fullpath] = method_names[0] + ":" + " ".join(method_bag)
                            i += 1

        print(f"\n\naggregate bag [{aggregate_bag}] \nsize {len(aggregate_bag)}")
        return files_to_words, method_to_words, files_to_method_calls, aggregate_bag

    def remove_non_determinative_words(self, set_to_diff: set):
        return set_to_diff.difference(self.java_keywords).difference(self.license_words) \
            .difference(self.common_methods).difference(self.common_english_words)


if __name__ == '__main__':

    start = time.perf_counter()
    scr = SourceCrawlerReducer()
    scr.clear_cached_crawler_data()
    files_to_words, method_to_words, files_to_method_calls, aggregate_bag = \
        scr.get_cached_crawler_data('/home/gpoor/cts-source')
    print(f"\n\nfiles_to_words  [{files_to_words}] \nsize {len(files_to_words)}")
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
