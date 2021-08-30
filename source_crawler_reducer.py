import os
import re


def find_test_files(reference_diction: dict):
    # traverse root directory, and list directories as dirs and files as files
    collected_value: dict = dict()
    for root, dirs, files in os.walk("/home/gpoor/cts-source"):
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
                            if len(value) > 4:
                                result = file_string.find(value)
                                if result > -1:
                                    print('{} found {} in  {}'.format(reference, value, fullpath))
                                    path_set.add(fullpath)
                        if len(path_set) > 0:
                            collected_value[reference] = ' '.join(path_set)
    return collected_value
    pass


# This should be used to find method declarations in files. Not hooked up yet.
def parse_(self, line_method):
    re_method = re.compile('(\w+?)\(\)')
    method_result = self.re_method.search(re_method)
    class_def = ""
    method = ""
    if method_result:
        method = method_result.group(0)
    else:
        re_class = re.compile('class (\w+)')
        class_result = self.re_class.search(re_class)
        if class_result:
            class_def = class_result.group(0)
    return class_def, method


def bag_from_text(text: str):
    file_string = re.sub("\s\s+", " ", text)
    split = file_string.split(" ")
    return set(split)


def make_bags_of_word():
    java_keywords = {'abstract', 'continue', 'for', 'new', 'switch', 'assert', '**', '*default', 'goto', '*', 'package',
                     'synchronized', 'boolean', 'do', 'if', 'private', 'this', 'break', 'double', 'implements',
                     'protected', 'throw', 'byte', 'else', 'import', 'public', 'throws', 'case', 'enum', '**', '**',
                     'instanceof', 'return', 'transient', 'catch', 'extends', 'int', 'short', 'try', 'char', 'final',
                     'interface', 'static', 'class', 'finally', 'long', 'strictfp', '**', 'volatile', 'const', '*',
                     'float', 'native', 'super', 'while', 'void'}
    common_methods = {'getFile', 'super', 'get', 'close', 'set', 'test', 'open', 'getType', 'getMessage', 'equals',
                      'not', 'find', 'search', 'length', 'size', 'getName'}
    license_words = bag_from_text(
        "/** **/ ** Copyright 2020 The Android Open Source Project * * Licensed under the Apache License, Version 2.0 (the  License); "
        "* you may not use this file except in compliance with the License. * You may obtain a copy of the License at ** "
        "http://www.apache.org/licenses/LICENSE-2.0 * * Unless required by applicable law or agreed to in writing, software * distributed under the License is distributed on an AS IS"
        " BASIS, * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. * See the License for the specific language governing permissions and * limitations "
        "under the License.(C) \"AS IS\" */")

    # traverse root directory, and list directories as dirs and files as files
    files_to_words: dict = dict()
    method_to_words: dict = dict()
    files_to_method_calls: dict = dict()
    aggregate_bag = set()
    method_call_re = re.compile('\w{3,40}(?=\(\w*\))(?!\s*?\{)')

    for root, dirs, files in os.walk("/home/gpoor/cts-source"):
        for file in files:
            if file.endswith('.java'):
                fullpath = '{}/{}'.format(root, file)
                with open(fullpath, "r") as text_file:
                    file_string = text_file.read()
                    text_file.close()

                    file_string = re.sub("\s\s+", " ", file_string)
                    # files to words
                    split = file_string.split(" ")
                    bag = set(split)
                    bag = bag.difference(java_keywords)
                    bag = bag.difference(license_words)
                    files_to_words[fullpath] = bag
                    # print(f'file {file} bag {bag}')
                    aggregate_bag.update(bag)

                    # get the names we want to search for to see if they are declared in other files
                    method_set = set(re.findall(method_call_re, file_string))
                    method_set = method_set.difference(common_methods)
                    files_to_method_calls[fullpath] = method_set

                    test_method_splits = re.split("@Test", file_string)
                    i = 1
                    while i < len(test_method_splits):

                        test_method_split = test_method_splits[i]
                        method_declare_body_splits = re.split('\s*public.+?\w+?(?=\(\w*?\))(?=.*?\{)',
                                                              test_method_split)
                        if len(method_declare_body_splits) > 1:
                            method_declare_body_split = method_declare_body_splits[1]
                            method_names = re.findall('\w{3,40}(?=\(:?\w*\))', test_method_split)

                            method_bag = set(method_declare_body_split.split(" ")).difference(java_keywords).difference(
                                license_words).difference(common_methods)
                            previous_value = method_to_words.get(fullpath)
                            if previous_value:
                                method_to_words[fullpath] = method_names[0] + ":" + " ".join(
                                    method_bag) + ' | ' + previous_value
                            else:
                                method_to_words[fullpath] = method_names[0] + ":" + " ".join(method_bag)

                        i += 1
    print(f"\n\naggregate bag [{aggregate_bag}] \nsize {len(aggregate_bag)}")
    return files_to_words, method_to_words, files_to_method_calls, aggregate_bag


if __name__ == '__main__':
    files_to_words, method_to_words, files_to_method_calls, aggregate_bag = make_bags_of_word()
    print(f"\n\naggregate bag [{aggregate_bag}] \nsize {len(aggregate_bag)}")
