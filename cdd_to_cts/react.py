import csv
import os
import os.path
import re
import sys
import time
import traceback
from pathlib import Path
from shutil import copyfile
from typing import Any

import rx
from rx import operators as ops, pipe
from rx.subject import ReplaySubject, BehaviorSubject

import helpers
import static_data
import table_ops
from cdd_to_cts.class_graph import parse_class_or_method, re_method
from cdd_to_cts.helpers import find_java_objects, add_list_to_count_dict, build_test_cases_module_dictionary, \
    raise_error, \
    convert_version_to_number_from_full_key, add_list_to_dict, remove_n_spaces_and_commas, CountDict
from cdd_to_cts.static_data import FULL_KEY_RE_WITH_ANCHOR, SECTION_ID_RE_STR, REQ_ID, SECTION_ID, REQUIREMENT, ROW, \
    FILE_NAME, FULL_KEY, SEARCH_TERMS, MATCHED_TERMS, CLASS_DEF, MODULE, QUALIFIED_METHOD, METHOD, HEADER_KEY, \
    MANUAL_SEARCH_TERMS, MATCHED_FILES, SEARCH_RESULT, PIPELINE_METHOD_TEXT
from cdd_to_cts.table_ops import write_table


def build_dict(key_req: str):
    row_dict = dict()
    key_req_spits = key_req.split(':', 1)
    row_dict[FULL_KEY] = key_req_spits[0]
    if len(key_req) < 2:
        row_dict[REQUIREMENT] = "None found"
        print("error build_dict " + key_req)
    else:
        row_dict[REQUIREMENT] = remove_n_spaces_and_commas(key_req_spits[1])
    return row_dict


def build_row(search_info_dict: dict, header: [str] = static_data.cdd_to_cts_app_header, do_log: bool = False):
    full_key = search_info_dict[FULL_KEY]
    key_split = full_key.split('/')
    search_info_dict[SECTION_ID] = key_split[0]
    if len(key_split) > 1:
        search_info_dict[REQ_ID] = key_split[1]

    row: [str] = list(header)
    try:
        for i in range(len(row)):
            row[i] = ''
        # Add any fields that are in the search
        row = dictionary_to_row(search_info_dict, header, row, do_log)

        search_result = search_info_dict.get(SEARCH_RESULT)
        if search_result:
            if len(search_result) > 0:
                dictionary_to_row(search_result, header, row, do_log)
                # After for loop for header row is built
        return row

    except Exception as err3:
        traceback.print_exc()
        raise_error("build_row: Exception ", err3)
    return None


def dictionary_to_row(row_values: dict, header_as_keys: [str], row: [str], do_log=True):
    cell_value = ""
    for key in header_as_keys:
        try:
            index = header_as_keys.index(key)
            if index > -1:
                value = row_values.get(key)
                if value:
                    if isinstance(value, str):
                        cell_value = value.strip()
                    elif isinstance(value, list):
                        cell_value = ' '.join(set(value))
                    elif isinstance(value, set):
                        cell_value = " ".join(value)
                    elif type(value) is dict:
                        cell_value = sorted({x for v in value.values() for x in v})
                    elif isinstance(value, CountDict) or isinstance(value, helpers.CountDict) or type(
                            value) == helpers.CountDict:
                        a_count_dict: CountDict = value
                        container_dict = a_count_dict.count_value_dict
                        if container_dict and len(container_dict) > 0:
                            try:
                                local_value = sorted(container_dict.items(), key=lambda x: x[1], reverse=True)
                                cell_value = local_value
                            except Exception as err1:
                                if do_log: print(
                                    f"build_row: Could not print values of {key} {str(container_dict)} {str(err1)}")
                    else:
                        cell_value = str(value).strip()
                    if len(cell_value) > 120000:
                        print(f"ERROR: row too long over 12000 {header_as_keys.index(key)}", file=sys.stderr)
                        cell_value = cell_value[0:120000]
                    row[index] = cell_value
        except (ValueError, IndexError) as err:
            if do_log: print(
                f"build_row: ValueError building row, expected when header and data mismatch {header_as_keys} vs {row_values}",
                err)
    return row


def write_table_from_dictionary(table_dict: dict, file_name: str, header: [str] = static_data.cdd_to_cts_app_header,
                                logging: bool = False) -> (dict, []):
    if file_name.find(static_data.WORKING_ROOT) == -1:
        file_name = static_data.WORKING_ROOT + file_name
    with open(file_name, 'w', newline='') as csv_output_file:
        table_writer = csv.writer(csv_output_file)
        # header = ','.join(table_dict.keys())
        if logging: print(f"header ={header}")
        table_writer.writerow(header)
        for key in table_dict:
            row_dict: dict = table_dict[key]
            row = build_row(row_dict, header, logging)
            table_writer.writerow(row)
        csv_output_file.close()

    return table_dict


def find_full_key_callable(record_id_split: [[int], str]) -> str:
    record_id_result = re.search(FULL_KEY_RE_WITH_ANCHOR, record_id_split)
    if record_id_result:
        record_id_string = record_id_result[0]
        record_id_string = record_id_string.replace("</a>", "")
        return rx.just("{}:{}".format(record_id_string.rstrip(']').lstrip('>'), record_id_split))
    return rx.just("")


def list_map(section_id: str, record_splits: list) -> list:
    dict_list = list()
    for record_split in record_splits:
        test_section_id = helpers.find_section_id(record_split)
        if test_section_id and len(test_section_id) > 0:
            section_id = test_section_id
        record_id_result = re.search(static_data.req_id_re_str, record_split)
        if record_id_result and record_id_result[0]:
            record_id = record_id_result[0].rstrip(']')
            dict_list.append('{}/{}:{}'.format(section_id, record_id, record_split))

    return dict_list


def add_to_dic(data: str, a_dic: dict):
    splits = data.split(':', 1)
    a_dic[splits[0]] = splits[1]


def observable_to_dict(obs: rx.Observable) -> dict:
    a_dic = dict()
    obs.subscribe(on_next=lambda table_line: add_to_dic(table_line, a_dic))
    return a_dic


def process_section(key_to_section: str):
    try:
        key_to_section_split = key_to_section.split(':', 1)
        section_id = key_to_section[0]
        section = helpers.remove_n_spaces_and_commas(key_to_section_split[1])
        req_id_splits = re.split('(?={})'.format(static_data.full_key_string_for_re), section)
        if req_id_splits and len(req_id_splits) > 1:
            return rx.for_in(req_id_splits, find_full_key_callable)
        else:
            req_id_splits = re.split(static_data.composite_key_string_re, str(section))
            if req_id_splits and len(req_id_splits) > 1:
                return rx.from_list(list_map(section_id, req_id_splits))  # build_composite_key_callable).pipe()
    except Exception as exception_process:
        helpers.raise_error(f" process_section {exception_process}", exception_process)
    return rx.empty()


def created_and_populated_search_info_from_row(full_key_row: [], header: []):
    search_info = dict()
    try:
        full_key: str = str(full_key_row[0]).strip()
        row: [] = full_key_row[1]
        search_info[ROW] = row
        for column in static_data.update_manual_header:
            try:
                index = header.index(column)
                search_info[column] = row[index]
            except:
                pass

        requirement: str = row[header.index(REQUIREMENT)]
        search_info[REQUIREMENT] = requirement
        java_objects = find_java_objects(requirement)
        search_info[HEADER_KEY] = header
        search_info[static_data.FULL_KEY] = full_key
        search_info[static_data.KEY_AS_NUMBER] = convert_version_to_number_from_full_key(full_key)
        key_split = full_key.split('/')
        search_term_set = set()
        section_req = set()
        section_req.add(full_key)
        section_req.add(key_split[0])
        if len(key_split) > 1:
            section_req.add(key_split[1])
        search_term_set.update(section_req)
        manual_search_terms = row[header.index(MANUAL_SEARCH_TERMS)]
        if manual_search_terms != "":
            add_list_to_dict(manual_search_terms, search_info, MANUAL_SEARCH_TERMS)
            search_term_set.update(set(manual_search_terms.split(' ')))
        # ToDo disabled search for anything but cdd java_object search_term_set.update(java_objects)
        search_info[static_data.SEARCH_TERMS] = search_term_set

    except Exception as err:
        helpers.raise_error(
            f"created_and_populated_search_info_from_row row=[{str()}] header[{str(header)}]  err =[{str(err)}] ", err)

    return search_info


class RxData:
    # rx_cts_files = rx.from_iterable(os.walk(CTS_SOURCE_ROOT))
    # rx_files_to_words = rx.from_iterable(sorted(files_to_words.items(), key=lambda x: x[1], reverse=True))
    # rx_method_to_words = rx.from_iterable(sorted(method_to_words.items(), key=lambda x: x[1], reverse=True))
    # rx_files_to_method_calls = rx.from_iterable(sorted(files_to_method_calls.items(), key=lambda x: x[1], reverse=True))
    # rx_at_test_files_to_methods = rx.from_iterable(
    #     sorted(at_test_files_to_methods.items(), key=lambda x: x[1], reverse=True))

    def __init__(self):
        self.max_matches = 100
        self.is_exact_match: bool = False

        self.match_count = 0
        self.start = time.perf_counter()
        self.end = time.perf_counter()
        self.__test_case_dict = None

        self.__input_table_keyed = None
        self.__input_header_keyed = None

        self.__list_of_at_test_files: set = set()

        self.__input_table = None
        self.__input_header = None
        self.__input_table_keys = None

        self.result_subject = BehaviorSubject("0:" + str(static_data.cdd_to_cts_app_header))
        self.__replay_input_table = None

        self.__replay_header = None
        self.__replay_at_test_files_to_methods = None
        self.__replay_cdd_requirements = None

    def cdd_html_to_requirements_csv(self, html_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE,
                                     output_file="output/htm_to_cdd.csv") -> rx.Observable:
        if html_file.find(static_data.WORKING_ROOT) == -1:
            html_file = static_data.WORKING_ROOT + html_file
        if output_file.find(static_data.WORKING_ROOT) == -1:
            output_file = static_data.WORKING_ROOT + output_file
        return self.get_cdd_html_to_requirements(html_file).pipe(
            ops.filter(lambda key_req: not key_req or len(key_req) < 2),
            ops.map(lambda key_req: build_dict(key_req)),
            ops.map(lambda v: build_row(v,
                                        static_data.cdd_info_only_header)),
            ops.to_list(),
            ops.map(
                lambda table: write_table(output_file,
                                          table,
                                          static_data.cdd_info_only_header)))

    def get_test_case_dict(self, table_dict_file=static_data.TEST_CASE_MODULES):
        # input_table, input_table_keys_to_index, input_header, duplicate_rows =
        if not self.__test_case_dict:
            self.__test_case_dict = build_test_cases_module_dictionary(table_dict_file)
        return self.__test_case_dict

    def get_input_table(self, table_dict_file=static_data.INPUT_TABLE_FILE_NAME_RX):
        # input_table, input_table_keys_to_index, input_header, duplicate_rows =
        if not self.__input_header:
            import table_ops
            self.__input_table, self.__input_table_keys, self.__input_header, duplicate_row = table_ops.read_table_sect_and_req_key(
                table_dict_file)
        return self.__input_table, self.__input_table_keys, self.__input_header

    def get_input_table_keyed(self, table_dict_file=static_data.INPUT_TABLE_FILE_NAME_RX):
        if not self.__input_table_keyed:
            import table_ops
            self.__input_table_keyed, self.__input_header_keyed = table_ops.read_table_to_dictionary(table_dict_file)
        return self.__input_table_keyed, self.__input_header_keyed

    def predicate(self, target) -> bool:
        # print("predicate " + str(target))
        result = self.execute_search_on_file_for_terms_return_results(target)
        if result.get(SEARCH_RESULT):
            self.result_subject.on_next(result)
            return True
        return False

    def execute_search_on_file_for_terms_return_results(self, search_info_and_file_tuple: tuple,
                                                        logging: bool = False) -> dict:
        # print("predicate " + str(target))
        # rx give us a tuple from combine latest, we want to bind them in one object that will get info in the stream and provide our result
        search_info: dict = search_info_and_file_tuple[0]

        try:
            # Get rid of tuple, change to a dict
            file_name = search_info_and_file_tuple[1]
            full_key = search_info.get(FULL_KEY)
            search_terms = search_info.get(SEARCH_TERMS)
            if not search_terms:
                search_terms = set()
            manual_search_terms = str(search_info.get(MANUAL_SEARCH_TERMS)).split(" ")
            if len(manual_search_terms) > 0 and len(manual_search_terms[0]) > 1:
                search_terms = set(search_terms).union(set(manual_search_terms))
            full_text_of_file_str = helpers.read_file_to_string(file_name)

            search_terms.difference_update(static_data.spurious_terms)
            if logging:
                print(f"searching {search_info_and_file_tuple[1]} \n for {str(search_terms)}")
            for matched_term in search_terms:
                matched_term = matched_term.strip(' ')


                if not matched_term:
                    continue
                # File search
                re_matches_from_file_search =  re.findall(re.escape(matched_term),full_text_of_file_str,flags=re.IGNORECASE)# full_text_of_file_str.count(matched_terms)

                is_found =len(re_matches_from_file_search) > 0
                if is_found:
                    if matched_term == search_info.get(FULL_KEY):
                        self.is_exact_match = True
                    cts_file_path_name = str(file_name).replace(static_data.CTS_SOURCE_ROOT + "/tests/", "")
                    search_result = search_info.get(SEARCH_RESULT)
                    if not search_result:
                        search_result = dict()
                    search_info[SEARCH_RESULT] = search_result
                    search_result[static_data.PIPELINE_FILE_NAME] = file_name
                    add_list_to_count_dict(cts_file_path_name, search_result, MATCHED_FILES)
                    for method_text in full_text_of_file_str.split("@Test"):
                       # index_of_term_in_method = method_text.find(matched_terms)
                        re_matches_from_method_search = re.findall(re.escape(matched_term), method_text,
                                                                 flags=re.IGNORECASE)  # full_text_of_file_str.count(matched_terms)

                        is_found = len(re_matches_from_file_search) > 0
                        if len(re_matches_from_method_search) > 0:
                            add_list_to_count_dict(cts_file_path_name, search_result, MATCHED_FILES)
                            add_list_to_count_dict(matched_term, search_result, MATCHED_TERMS)
                            subset_text = self.find_method_text_subset(len(re_matches_from_method_search), method_text)
                            # add_list_to_count_dict(subset_text, search_result, static_data.METHOD_TEXT)#," || ")
                            method_text_str = f"([{len(re_matches_from_method_search)}:{cts_file_path_name}]:[{matched_term}]:[{len(re_matches_from_method_search)}]:method_text:[{subset_text}])"
                            add_list_to_count_dict(method_text_str, search_result,
                                                   static_data.METHODS_STRING)  # ," || ")
                            search_result[FILE_NAME] = cts_file_path_name
                            search_result[
                                PIPELINE_METHOD_TEXT] = method_text  # Because this is used in find find_data_for_csv_dict
                            self.find_data_for_csv_dict(search_info)
                            if logging:
                                print(f"Found match {str(search_result)}")
                            # result = f'["{a_list_item}",["{mi}":"{method_text}"]]'
                            # print(f"\n matched: {result}")
                if self.is_exact_match:
                    break
            # end for search terms

        except Exception as err:
            raise_error(f"execute_search_on_file_for_terms_return_results [{str(search_info)}] ", err)

        return search_info

    def find_method_text_subset(self, index_of_term_in_method, method_text):
        method_text_len = len(method_text)
        if method_text_len > 50:
            if index_of_term_in_method + 25 < method_text_len:
                end_mark = index_of_term_in_method
                start_mark = end_mark - 50
            else:
                end_mark = method_text_len - 1
                start_mark = end_mark - 50
            if start_mark < 0:
                start_mark = 0
            subset_text = method_text[start_mark:end_mark]
        else:
            subset_text = method_text
        subset_text = subset_text.replace('\n', '')
        return subset_text

    def find_data_for_csv_dict(self, search_info: dict, logging: bool = False) -> dict:

        full_key = "0/0"
        method_text = ''
        test_case_name = ""
        method = ""

        try:

            # search_terms = search_info.get('search_terms')
            full_key = search_info.get(FULL_KEY)
            search_result = search_info.get(SEARCH_RESULT)
            if search_result:
                file_name = search_result.get(static_data.PIPELINE_FILE_NAME)
                try:
                    method_text = search_result.get(PIPELINE_METHOD_TEXT)
                    method_result = re_method.search(method_text, 1)
                    if method_result and method_result.group(0) and method_result.group(0) != '':
                        method = method_result.group(0)
                        add_list_to_count_dict(method, search_result, METHOD)
                    else:
                        method = ""
                        # ToDo figure out adding to the dictionary

                except Exception as err:
                    print("Not fatal but should improve exception find_data_for_csv_dict " + str(err))
                if logging: print(f'Could not find {static_data.METHOD_RE} in text [{method_text}]')
                class_name_split_src = file_name.split('/src/')
                # Module
                if len(class_name_split_src) > 0:
                    import class_graph
                    test_case_name = class_graph.test_case_name(class_name_split_src[0],
                                                                self.get_test_case_dict())
                    add_list_to_count_dict(test_case_name, search_result, MODULE)

                if len(class_name_split_src) > 1:
                    class_name = str(class_name_split_src[1]).replace("/", ".").rstrip(".java")
                    add_list_to_count_dict(class_name, search_result, CLASS_DEF)
                    if method.find('Test') != -1 or method.find('test') != -1:
                        qualified_method = f"{test_case_name}:{class_name}.{method}"
                        add_list_to_dict(qualified_method, search_result, QUALIFIED_METHOD)
                        self.match_count += 1
                    else:
                        # result = re.search(r'\s*public.+?\w+?(?=\(\w*?\))(?=.*?{)', method_text)
                        print(f"result No method with test in the name.")

        except Exception as e:
            helpers.raise_error(f"find_data_for_csv_dict at {full_key}", e)

        return search_info

    def get_replay_of_at_test_files_only(self,
                                         results_grep_at_test: str = (
                                                 "%s" % static_data.TEST_FILES_TXT),
                                         scheduler: rx.typing.Scheduler = None) -> rx.Observable:

        return self.get_replay_of_at_test_files(results_grep_at_test, scheduler).pipe(
            ops.map(lambda target: target.split(' :')[0]), ops.distinct())

    def get_replay_of_at_test_files(self,
                                    results_grep_at_test: str = ("%s" % static_data.TEST_FILES_TXT),
                                    scheduler: rx.typing.Scheduler = None) -> ReplaySubject:

        if self.__replay_at_test_files_to_methods:
            # print( f"Warning get_replay_of_at_test_files() ignoring input file {results_grep_at_test} in to use cashed data")
            return self.__replay_at_test_files_to_methods
        else:
            self.__replay_at_test_files_to_methods = ReplaySubject(9999, scheduler=scheduler)
        if results_grep_at_test.find(static_data.WORKING_ROOT) == -1:
            results_grep_at_test = static_data.WORKING_ROOT + results_grep_at_test
        re_annotations = re.compile('@Test.*?$')
        try:
            with open(results_grep_at_test, "r") as grep_of_test_files:
                file_content = grep_of_test_files.readlines()
                count = 0
                while count < len(file_content):
                    line = file_content[count]
                    count += 1
                    result = re_annotations.search(line)
                    # Skip lines without annotations
                    if result:
                        test_annotated_file_name_absolute_path = line.split(":")[0]
                        # test_annotated_file_name = get_cts_root(test_annotated_file_name_absolute_path)
                        # requirement = result.group(0)
                        # noinspection DuplicatedCode
                        line_method = file_content.pop()
                        count += 1
                        class_def, method = parse_class_or_method(line_method)
                        if class_def == "" and method == "":
                            line_method = file_content.pop()
                            count += 1
                            class_def, method = parse_class_or_method(line_method)
                        if method:
                            self.__replay_at_test_files_to_methods.on_next(
                                '{} :{}'.format(test_annotated_file_name_absolute_path, method.strip(' ')))

                self.__replay_at_test_files_to_methods.on_completed()
                return self.__replay_at_test_files_to_methods
        except FileNotFoundError as e:
            raise helpers.raise_error(f" Could not find {results_grep_at_test} ", e)

    def get_list_of_at_test_files(self,
                                  results_grep_at_test: str = ("%s" % static_data.TEST_FILES_TXT)) -> set:
        if results_grep_at_test.find(static_data.WORKING_ROOT) == -1:
            results_grep_at_test = static_data.WORKING_ROOT + results_grep_at_test
        if len(self.__list_of_at_test_files) > 0:
            # print(f"Warning get_replay_of_at_test_files() ignoring input file {results_grep_at_test} in to use cashed data")
            return self.__list_of_at_test_files
        else:
            re_annotations = re.compile('@Test.*?$')
            try:
                with open(results_grep_at_test, "r") as grep_of_test_files:
                    file_content = grep_of_test_files.readlines()
                    count = 0
                    while count < len(file_content):
                        line = file_content[count]
                        count += 1
                        result = re_annotations.search(line)
                        # Skip lines without annotations
                        if result:
                            test_annotated_file_name_absolute_path = line.split(":")[0]
                            # test_annotated_file_name = get_cts_root(test_annotated_file_name_absolute_path)
                            # requirement = result.group(0)
                            # noinspection DuplicatedCode
                            line_method = file_content.pop()
                            count += 1
                            class_def, method = parse_class_or_method(line_method)
                            if class_def == "" and method == "":
                                line_method = file_content.pop()
                                count += 1
                                class_def, method = parse_class_or_method(line_method)
                            if method:
                                self.__list_of_at_test_files.add(format(test_annotated_file_name_absolute_path))

                    return self.__list_of_at_test_files
            except FileNotFoundError as e:
                raise helpers.raise_error(f" Could not find {results_grep_at_test} ", e)

    def get_replay_read_table(self, file_name: str = static_data.INPUT_TABLE_FILE_NAME_RX) -> [ReplaySubject,
                                                                                               ReplaySubject]:

        if self.__replay_input_table and self.__replay_header:
            return self.__replay_input_table, self.__replay_header
        else:
            self.__replay_input_table = ReplaySubject(1500)
            self.__replay_header = ReplaySubject(50)

        section_id_index = 1
        req_id_index = 2
        duplicate_rows: [str, str] = dict()
        if file_name.find(static_data.WORKING_ROOT) == -1:
            file_name = static_data.WORKING_ROOT + file_name
        try:
            with open(file_name) as csv_file:

                csv_reader_instance: [str] = csv.reader(csv_file, delimiter=',')
                table_index = 0

                for row in csv_reader_instance:
                    if table_index == 0:
                        try:
                            section_id_index = row.index(SECTION_ID)
                            req_id_index = row.index(REQ_ID)
                            print(f'Found header for {file_name} names are {", ".join(row)}')
                            self.__replay_header.on_next(row)
                            self.__replay_header.on_completed()
                            table_index += 1

                            # Skip the rest of the loop... if there is an exception carry on and get the first row
                            continue
                        except ValueError:
                            message = f' Error: First row NOT header {row} default to section_id = col 1 and req_id col 2. First row of file {csv_file} should contain CSV with header like Section, section_id, etc looking for <Section> not found in {row}'
                            print(message)
                            raise SystemExit(message)
                            # Carry on and get the first row

                    # Section,section_id,req_id
                    section_id_value = row[section_id_index].rstrip('.')
                    req_id_value = row[req_id_index]
                    if len(req_id_value) > 0:
                        key_value = '{}/{}'.format(section_id_value, req_id_value)
                    elif len(section_id_value) > 0:
                        key_value = section_id_value

                    self.__replay_input_table.on_next(f'{key_value}:{row}')

                if len(duplicate_rows) > 0:
                    print(
                        f"ERROR, reading tables with duplicate 1 {file_name} has={len(duplicate_rows)} duplicates {duplicate_rows} ")

            self.__replay_input_table.on_completed()

            return self.__replay_input_table, self.__replay_header
        except IOError as e:
            helpers.raise_error(f"Failed to open file {file_name} exception -= {type(e)} exiting...")

    def get_filtered_cdd_by_table(self, input_table_file=static_data.INPUT_TABLE_FILE_NAME_RX,
                                  cdd_requirements_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE,
                                  scheduler: rx.typing.Scheduler = None) -> rx.Observable:

        table_dic = observable_to_dict(self.get_replay_read_table(input_table_file)[0])
        return self.get_cdd_html_to_requirements(cdd_requirements_file, scheduler) \
            .pipe(ops.filter(lambda v: table_dic.get(str(v).split(':', 1)[0])))

    def get_cdd_html_to_requirements(self, cdd_html_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE,
                                     scheduler: rx.typing.Scheduler = None):

        if not self.__replay_cdd_requirements:
            self.__replay_cdd_requirements = ReplaySubject(buffer_size=2000, scheduler=scheduler)
            if cdd_html_file.find(static_data.WORKING_ROOT) == -1:
                cdd_html_file = static_data.WORKING_ROOT + cdd_html_file

            with open(cdd_html_file, "r") as text_file:
                cdd_requirements_file_as_string = text_file.read()
                section_id_re_str: str = SECTION_ID_RE_STR
                cdd_sections_splits = re.split('(?={})'.format(section_id_re_str), cdd_requirements_file_as_string,
                                               flags=re.DOTALL)
                # Start at 0 to don't skip for tests and unknown input
                for i in range(0, len(cdd_sections_splits)):
                    section = cdd_sections_splits[i]
                    cdd_section_id = helpers.find_section_id(section)
                    if cdd_section_id:
                        if '13' == cdd_section_id:
                            # section 13 is "Contact us" and has characters that cause issues at lest for git
                            print(f"Warning skipping section 13 just the end no requirments")
                            continue
                        section = re.sub('\s\s+', ' ', section)
                        section = section.replace("<\a>", "")
                        self.__replay_cdd_requirements.on_next('{}:{}'.format(cdd_section_id, section))
            self.__replay_cdd_requirements.on_completed()
            # if all ready read, just return it.
        return self.__replay_cdd_requirements.pipe(
            ops.flat_map(lambda section_and_key: process_section(section_and_key)))

    def get_at_test_method_words(self, test_file_grep_results=static_data.TEST_FILES_TXT,
                                 scheduler: rx.typing.Scheduler = None):
        return self.get_replay_of_at_test_files(test_file_grep_results, scheduler).pipe(
            ops.map(lambda v: str(v).split(" :")[0]),
            ops.distinct_until_changed(),
            ops.map(lambda f:
                    f'{f}:{helpers.read_file_to_string(f)}'))

    @staticmethod
    def get_pipe_create_results_table():
        return pipe(
            # ops.filter(lambda search_info: dict(search_info).get(SEARCH_RESULT)),
            ops.map(lambda search_info: build_row(search_info, header=static_data.cdd_to_cts_app_header,
                                                  do_log=True)),
            ops.to_list()
        )

    def main_do_create_table(self, input_table_file=static_data.INPUT_TABLE_FILE_NAME_RX,
                             # cdd_requirements_file: str = static_data.CDD_REQUIREMENTS_FROM_HTML_FILE,
                             output_file: str = "output/output_built_table.csv",
                             output_header: str = static_data.cdd_to_cts_app_header,
                             scheduler: rx.typing.Scheduler = None):
        table_dict, header = self.get_input_table_keyed(input_table_file)
        return self.do_search(table_dict, header, scheduler).pipe(
            self.get_pipe_create_results_table(),
            ops.map(lambda table: table_ops.write_table(output_file, table, output_header)))

    def do_search(self, table_dict: dict, header: [], scheduler: rx.typing.Scheduler = None):

        return rx.from_iterable(table_dict, scheduler).pipe(ops.map(lambda key: (key, table_dict.get(key))),
                                                            ops.map(lambda
                                                                        full_key_row: created_and_populated_search_info_from_row(
                                                                full_key_row, header)),
                                                            ops.map(
                                                                lambda search_info: self.search_on_files(search_info)))

    def search_on_files(self, search_info, logging: bool = True):
        list_of_test_files = self.get_list_of_at_test_files()
        if logging:
            self.end = time.perf_counter()
            print(f'elapsed {self.end - self.start:0.4f}sec ')
            print(
                f'search key [{str(search_info.get(FULL_KEY))}] for [{search_info.get(SEARCH_TERMS)}] against {len(list_of_test_files)} files')
        # input("Do you want to continue?")
        self.match_count = 0
        search_root = ""
        try:
            row = search_info.get(ROW)
            search_root = row[static_data.cdd_to_cts_app_header.index(static_data.SEARCH_ROOTS)]
        except:
            pass
        self.is_exact_match = False
        for file_to_search in list_of_test_files:
            # if there is not filter data OR the filter is match search
            if ((not search_root) or (len(search_root) == 0)) or (file_to_search.find(search_root) != -1):
                if self.match_count > self.max_matches:
                    print(f"Note: limiting matches to {self.max_matches} skipping {file_to_search}")
                else:
                    self.execute_search_on_file_for_terms_return_results((search_info, file_to_search))
            if self.is_exact_match:
                break
        return search_info


def my_print(v, f: Any = '{}'):
    print(f.format(v))
    return v


if __name__ == '__main__':
    start = time.perf_counter()
    rd = RxData()
    rd.max_matches = 200
    result_table = [[str]]

    input_file_name_s = "input/created_output_w_manual.csv"
    input_file_name_oplus = "input/input_table_key_index_mod.csv"
    original_source_csv = "input/input_table_key_index_mod.csv"
    ##  input_file_name ="input/output_from_input.csv"
    test_output_file_name = "output/test_output_from_input.csv"
    input_file_name = "input/oplus-5.1.csv"
    output_file_name = "output/oplus-5.1.csv"

    input_file = Path(static_data.WORKING_ROOT + output_file_name)
    # if not input_file.exists():
    #     copyfile(static_data.WORKING_ROOT + original_source_csv, static_data.WORKING_ROOT + output_file_name)
    #     print("Expected first time through")

    rd.main_do_create_table(input_file_name,output_file_name).subscribe(
        on_next=lambda table: my_print("that's all folks!{} "),
        on_completed=lambda: print("completed"),
        on_error=lambda err: helpers.raise_error("in main", err))
    # copyfile(static_data.WORKING_ROOT+output_file_name, static_data.WORKING_ROOT+input_file_name)
    # rx.from_iterable(test_dic).subscribe( lambda value: print("Received {0".format(value)))
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
