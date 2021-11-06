import csv
import re
import sys
import time
import traceback
from typing import Any

import rx
from rx import operators as ops, pipe
from rx.subject import ReplaySubject, BehaviorSubject

import class_graph
import helpers
import static_data
import table_ops
from cdd_to_cts.class_graph import parse_class_or_method, re_method
from cdd_to_cts.helpers import find_java_objects, add_list_to_count_dict, build_test_cases_module_dictionary, \
    raise_error, \
    convert_version_to_number_from_full_key, CountDict
from cdd_to_cts.static_data import full_key_string_for_re, SECTION, REQ_ID, SECTION_ID, REQUIREMENT, ROW, \
    FILE_NAME, FULL_KEY, SEARCH_TERMS, MATCHED_TERMS, CLASS_DEF, MODULE, QUALIFIED_METHOD, METHOD, HEADER_KEY, \
    MANUAL_SEARCH_TERMS, MATCHED_FILES, SEARCH_RESULT, PIPELINE_METHOD_TEXT, FLAT_RESULT, TEST_AVAILABILITY
from update_release import update_release_table_with_changes


def build_dict(key_req: str):
    row_dict = dict()
    key_req_spits = key_req.split(':', 1)
    row_dict[FULL_KEY] = key_req_spits[0]
    if len(key_req) < 2:
        row_dict[REQUIREMENT] = "None found"
        print("error build_dict " + key_req)
    else:
        row_dict[REQUIREMENT] = helpers.remove_n_spaces_and_delimiter(key_req_spits[1])
    return row_dict


def build_row(search_info_dict: dict, header: [str] = static_data.cdd_to_cts_app_header, do_log: bool = False):
    full_key = search_info_dict[FULL_KEY]
    key_split = full_key.split('/')
    search_info_dict[SECTION_ID] = key_split[0]
    if len(key_split) > 1:
        search_info_dict[REQ_ID] = key_split[1]
    row_data = search_info_dict[ROW]
    search_info_dict[SECTION] = row_data[header.index(SECTION)]

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
                                cell_value = f'{local_value}'
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
    file_name = helpers.find_valid_path(file_name)

    with open(file_name, 'w', newline=static_data.table_newline) as csv_output_file:
        table_writer = csv.writer(csv_output_file, quoting=csv.QUOTE_ALL, delimiter=static_data.table_delimiter)
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
    record_id_result = re.search(full_key_string_for_re, record_id_split)
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
        section = helpers.remove_n_spaces_and_delimiter(key_to_section_split[1])
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


def created_and_populated_search_info_from_key_row_tuple(tuple_of_key_and_row: [str, [str]], header: [str],
                                                         columns_to_copy: [
                                                             str] = static_data.fields_for_search_info_header) -> dict:
    search_info = dict()
    try:
        full_key: str = str(tuple_of_key_and_row[0]).strip()
        row: [] = tuple_of_key_and_row[1]
        search_info[ROW] = row

        header_as_string = " ".join(header)
        for column in columns_to_copy:
            if header_as_string.find(column) != -1:
                index = header.index(column)
                search_info[column] = row[index]

        urls = helpers.find_urls(search_info[REQUIREMENT])
        if len(urls) > 0:
            search_info[static_data.URLS] = urls

        search_info[HEADER_KEY] = header
        search_info[static_data.FULL_KEY] = full_key
        search_info[static_data.KEY_AS_NUMBER] = convert_version_to_number_from_full_key(full_key)
        return search_info


    except Exception as err:
        helpers.raise_error(
            f"created_and_populated_search_info_from_key_row_tuple row=[{str()}] header[{str(header)}]  err =[{str(err)}] ",
            err)

    return search_info


def find_method_text_subset(search_string: str, method_text: str) -> str:
    method_text_len = len(method_text)
    first_re_match_from_method_search = re.search(search_string, method_text, flags=re.IGNORECASE)
    if not first_re_match_from_method_search:
        return ""
    index_of_term_in_method = first_re_match_from_method_search.endpos
    target_length = 100
    half_target_length = int(target_length / 2)
    if method_text_len > target_length:
        if index_of_term_in_method + half_target_length < method_text_len:
            end_mark = index_of_term_in_method + half_target_length
            start_mark = end_mark - target_length
        else:
            end_mark = method_text_len - 1
            start_mark = end_mark - target_length
        if start_mark < 0:
            start_mark = 0
        subset_text = method_text[start_mark:end_mark]
    else:
        subset_text = method_text
    subset_text = subset_text.replace('\n', '')
    return subset_text


def find_search_terms(search_info) -> dict:
    full_key = search_info.get(FULL_KEY)
    requirement = search_info.get(REQUIREMENT)
    auto_search_terms = find_java_objects(requirement)

    key_split = full_key.split('/')
    section_req = set()
    section_req.add(full_key)
    section_req.add(key_split[0])
    if len(key_split) > 1:
        req_search = re.escape(key_split[1])
        req_search = static_data.re_tag + "(?<!/)" + req_search
        section_req.add(req_search)
    search_info[static_data.AUTO_SEARCH_TERMS] = auto_search_terms

    manual_search_terms = set(str(search_info.get(MANUAL_SEARCH_TERMS)).split(" "))
    search_term_set = set()
    # ToDo Restore full search?
    search_term_set.update(manual_search_terms)
    # Section requirements search on or off
    search_term_set.update(section_req)
    search_term_set.update(auto_search_terms)
    search_term_set.difference_update(static_data.spurious_terms)
    search_info[static_data.SEARCH_TERMS] = search_term_set
    return search_info


def conditional_re_escape(matched_term):
    if not matched_term.startswith(static_data.re_tag):
        search_string = re.escape(matched_term)
    else:
        search_string = matched_term.removeprefix(static_data.re_tag)
    return search_string


class RxData:
    # rx_cts_files = rx.from_iterable(os.walk(CTS_SOURCE_ROOT))
    # rx_files_to_words = rx.from_iterable(sorted(files_to_words.items(), key=lambda x: x[1], reverse=True))
    # rx_method_to_words = rx.from_iterable(sorted(method_to_words.items(), key=lambda x: x[1], reverse=True))
    # rx_files_to_method_calls = rx.from_iterable(sorted(files_to_method_calls.items(), key=lambda x: x[1], reverse=True))
    # rx_at_test_files_to_methods = rx.from_iterable(
    #     sorted(at_test_files_to_methods.items(), key=lambda x: x[1], reverse=True))

    def __init__(self) -> None:
        self.max_matches = 100
        self.progress_count = 0
        self.is_exact_match: bool = False

        self.match_count = 0
        self.start = time.perf_counter()
        self.end = time.perf_counter()
        self.__test_case_dict = None

        self.__input_table_keyed = None
        self.__input_header_keyed = None

        self.__list_of_at_test_files: set = set()

        self.result_subject = BehaviorSubject(dict())
        self.__replay_input_table = None

        self.__replay_header = None
        self.__replay_at_test_files_to_methods = None
        self.__replay_cdd_requirements = None

        self.__dependency_dictionary = class_graph.parse_dependency_file()

    # Not in use
    # def cdd_html_to_requirements_csv(self, html_file :str,
    #                                  output_file: str) -> rx.Observable:
    #     html_file = helpers.find_valid_path(html_file)
    #     output_file = helpers.find_valid_path(output_file)
    #
    #     return self.get_cdd_html_to_requirements(html_file).pipe(
    #         ops.filter(lambda key_req: not key_req or len(key_req) < 2),
    #         ops.map(lambda key_req: build_dict(key_req)),
    #         ops.map(lambda v: build_row(v,
    #                                     static_data.cdd_info_only_header)),
    #         ops.to_list(),
    #         ops.map(
    #             lambda table: table_ops.write_table(output_file,
    #                                       table,
    #                                       static_data.cdd_info_only_header)))

    def get_test_case_dict(self, table_dict_file=static_data.TEST_CASE_MODULES):
        if not self.__test_case_dict:
            self.__test_case_dict = build_test_cases_module_dictionary(table_dict_file)
        return self.__test_case_dict

    def init_input_table_keyed(self, table_dict_file):
        import table_ops
        self.__input_table_keyed, self.__input_header_keyed = table_ops.read_table_to_dictionary(table_dict_file)
        return self.__input_table_keyed, self.__input_header_keyed

    def get_input_table_keyed(self):
        if not self.__input_table_keyed:
            self.init_input_table_keyed(static_data.INPUT_TABLE_FILE_NAME_RX)
        return self.__input_table_keyed, self.__input_header_keyed

    def execute_search_on_file_for_terms_return_results(self, search_info_and_file_tuple: tuple,
                                                        logging: bool = False) -> dict:
        # print("predicate " + str(target))
        # rx give us a tuple from combine latest, we want to bind them in one object that will get info in the stream and provide our result
        search_info: dict = search_info_and_file_tuple[0]
        try:
            # Get rid of tuple, change to a dict
            file_name_param = search_info_and_file_tuple[1]

            search_terms = search_info.get(SEARCH_TERMS)

            full_text_of_file_str = helpers.read_file_to_string(file_name_param).replace('\t', ' ')

            if logging:
                print(f"searching {search_info_and_file_tuple[1]} \n for {str(search_terms)}")
            for matched_term in search_terms:
                matched_term: str = matched_term.strip(' ')

                if not matched_term:
                    continue
                # File search
                search_string = conditional_re_escape(matched_term)
                search_string = search_string.replace("&", ".*")

                re_matches_from_file_search = re.findall(search_string, full_text_of_file_str,
                                                         flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)  # full_text_of_file_str.count(matched_terms)
                match_count_of_term_in_file = len(re_matches_from_file_search)
                is_found = match_count_of_term_in_file > 0
                if is_found:
                    if matched_term == search_info.get(FULL_KEY):
                        self.is_exact_match = True
                    cts_file_path_name = str(file_name_param).partition('src')[2]
                    search_result = search_info.get(SEARCH_RESULT)
                    if not search_result:
                        search_result = dict()
                    search_info[SEARCH_RESULT] = search_result
                    flat_result = dict()
                    search_result[FLAT_RESULT] = flat_result
                    flat_result[REQUIREMENT] = search_info[REQUIREMENT]
                    flat_result[SEARCH_TERMS] = search_info[SEARCH_TERMS]

                    search_result[static_data.PIPELINE_FILE_NAME] = file_name_param
                    add_list_to_count_dict(f"({match_count_of_term_in_file},{matched_term},{cts_file_path_name})",
                                           search_result, MATCHED_FILES)
                    method_text_splits_of_file = full_text_of_file_str.split("@Test")
                    prepend = ""
                    if len(method_text_splits_of_file) <= 1:
                        method_text_splits_of_file = method_text_splits_of_file = full_text_of_file_str.split(
                            static_data.not_annotated_test_start)
                        prepend = static_data.not_annotated_test_start
                    for method_text in method_text_splits_of_file:
                        method_text = prepend + method_text
                        re_matches_from_method_search = re.findall(search_string, method_text,
                                                                   flags=re.IGNORECASE)  # full_text_of_file_str.count(matched_terms)
                        if len(re_matches_from_method_search) > 0:
                            add_list_to_count_dict(file_name_param, search_result, FILE_NAME)
                            flat_result[FILE_NAME] = file_name_param
                            add_list_to_count_dict(matched_term, search_result, MATCHED_TERMS)
                            flat_result[MATCHED_TERMS] = matched_term
                            subset_text = find_method_text_subset(search_string, method_text)
                            # add_list_to_count_dict(subset_text, search_result, static_data.METHOD_TEXT)#," || ")
                            method_text_str = f"([{len(re_matches_from_method_search)}:{cts_file_path_name}]:[{matched_term}]:[{len(re_matches_from_method_search)}]:method_text:[{subset_text}])"
                            add_list_to_count_dict(method_text_str, search_result,
                                                   static_data.METHODS_STRING)  # ," || ")
                            flat_result[static_data.METHODS_STRING] = method_text
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

    def find_data_for_csv_dict(self, search_info: dict, logging: bool = False) -> dict:

        full_key = "0/0"
        method_text = ''
        # test_case_name = ""
        # method = ""

        try:

            # search_terms = search_info.get('search_terms')
            full_key = search_info.get(FULL_KEY)
            search_result = search_info.get(SEARCH_RESULT)
            if search_result:
                flat_result = search_result.get(FLAT_RESULT)
                file_name = search_result.get(static_data.PIPELINE_FILE_NAME)
                class_name_split_src = file_name.split('/src/')
                # Module
                if len(class_name_split_src) > 0:

                    import class_graph
                    test_case_name = class_graph.search_for_test_case_name(file_name,
                                                                           self.get_test_case_dict())
                    add_list_to_count_dict(test_case_name, search_result, static_data.MODULES)
                    search_result[MODULE] = test_case_name  # This will just get the last module, overwriting
                    flat_result[MODULE] = test_case_name

                    if len(class_name_split_src) > 1:
                        class_name = str(class_name_split_src[1]).replace("/", ".").rstrip(".java")
                        add_list_to_count_dict(class_name, search_result, static_data.CLASS_DEFS)
                        search_result[CLASS_DEF] = class_name  # This will just get the last class_def, overwriting

                        flat_result[CLASS_DEF] = class_name

                        try:
                            method_text = search_result.get(PIPELINE_METHOD_TEXT)
                            method_results = re_method.findall(method_text)
                            if method_results and len(method_results) > 0:
                                for method in method_results:
                                    if method.lower().find('is') != -1 or method.lower().find('test') != -1:
                                        qualified_method = f"[{class_name} {method} {test_case_name}]"
                                        add_list_to_count_dict(qualified_method, search_result, QUALIFIED_METHOD)
                                        flat_result[METHOD] = method
                                        self.match_count += 1
                                        break
                                    else:
                                        flat_result[METHOD] = method
                                        # result = re.search(r'\s*public.+?\w+?(?=\(\w*?\))(?=.*?{)', method_text)
                                        # ToDo search dependencies
                                        if logging: print(f"result No method with test in the name {method}.")

                                    add_list_to_count_dict(method, search_result, static_data.METHODS)
                                    search_result[METHOD] = method # This will just get the last method, overwriting
                            else:
                                method = ""
                                # ToDo figure out adding to the dictionary

                        except Exception as err:
                            print("Not fatal but should improve exception find_data_for_csv_dict " + str(err))
                            if logging: print(f'Could not find {static_data.METHOD_RE} in text [{method_text}]')

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
            self.__replay_at_test_files_to_methods.pipe(
                rx.from_list(self.get_list_of_at_test_files(results_grep_at_test)))

    def get_list_of_at_test_files(self,
                                  results_grep_at_test: str = ("%s" % static_data.TEST_FILES_TXT)) -> set:

        results_grep_at_test = helpers.find_valid_path(results_grep_at_test)

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

    #
    # def get_cdd_html_to_requirements(self, cdd_html_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE,
    #                                  scheduler: rx.typing.Scheduler = None):
    #
    #     if not self.__replay_cdd_requirements:
    #         self.__replay_cdd_requirements = ReplaySubject(buffer_size=2000, scheduler=scheduler)
    #         cdd_html_file = helpers.find_valid_path(cdd_html_file)
    #
    #         with open(cdd_html_file, "r") as text_file:
    #             cdd_requirements_file_as_string = text_file.read()
    #             #  section_re_str: str = r'"(?:\d{1,3}_)+'
    #             section_marker: str = "data-text=\"\s*"
    #             section_re_str: str = section_marker + static_data.SECTION_ID_RE_STR
    #             cdd_sections_splits = re.split('(?={})'.format(section_re_str), cdd_requirements_file_as_string,
    #                                            flags=re.DOTALL)
    #             # Start at 0 to don't skip for tests and unknown input
    #             for i in range(0, len(cdd_sections_splits)):
    #                 section = cdd_sections_splits[i]
    #                 cdd_section_id = helpers.find_section_id(section)
    #                 if cdd_section_id:
    #                     if '13' == cdd_section_id:
    #                         # section 13 is "Contact us" and has characters that cause issues at lest for git
    #                         print(f"Warning skipping section 13 just the end no requirements")
    #                         continue
    #                     section = re.sub('\s\s+', ' ', section)
    #                     section = section.replace("<\a>", "")
    #                     self.__replay_cdd_requirements.on_next('{}:{}'.format(cdd_section_id, section))
    #         self.__replay_cdd_requirements.on_completed()
    #         # if all ready read, just return it.
    #     return self.__replay_cdd_requirements.pipe(
    #         ops.flat_map(lambda section_and_key: process_section(section_and_key)))

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
                             output_file: str = static_data.RX_WORKING_OUTPUT_TABLE_TO_EDIT,
                             scheduler: rx.typing.Scheduler = None):
        self.__input_table_keyed, self.__input_header_keyed = self.init_input_table_keyed(input_table_file)

        return self.do_search(self.__input_table_keyed, self.__input_header_keyed, scheduler).pipe(
            self.get_pipe_create_results_table(),
            ops.map(lambda table: table_ops.write_table(output_file, table, self.__input_header_keyed)))

    def do_search(self, table_dict: dict, header: [], scheduler: rx.typing.Scheduler = None):

        return rx.from_iterable(table_dict, scheduler).pipe(ops.map(lambda key: (key, table_dict.get(key))),
                                                            ops.map(lambda
                                                                        full_key_row: created_and_populated_search_info_from_key_row_tuple(
                                                                full_key_row, header)),
                                                            ops.filter(lambda search_info: search_info.get(
                                                                static_data.TEST_AVAILABILITY) == ""),
                                                            ops.map(lambda search_info: find_search_terms(search_info)),
                                                            ops.map(
                                                                lambda search_info: self.search_on_files(search_info)),
                                                            ops.map(
                                                                lambda search_info: self.publish_each_result(search_info))
                                                            )

    def do_on_complete(self):
        self.result_subject.on_completed()
        pass

    def search_on_files(self, search_info: dict, logging: bool = True) -> dict:
        list_of_test_files = self.get_list_of_at_test_files()
        list_of_test_files = list_of_test_files.union(helpers.get_list_void_public_test_files())
        self.progress_count += 1
        skip_count = 0
        search_root = ""
        row = search_info.get(ROW)
        try:
            search_root = row[static_data.cdd_to_cts_app_header.index(static_data.SEARCH_ROOTS)]
        except:
            pass
        try:
            not_search_terms = set(
                row[static_data.cdd_to_cts_app_header.index(static_data.NOT_SEARCH_TERMS)].split(' '))
            search_info[SEARCH_TERMS].difference_update(not_search_terms)
        except:
            pass

        if logging:
            self.end = time.perf_counter()
            print(f'\n {self.progress_count}) of {len(self.__input_table_keyed)} ')
            print(f'elapsed {self.end - self.start:0.4f}sec ')
            print(
                f'search key [{str(search_info.get(FULL_KEY))}] for [{search_info.get(SEARCH_TERMS)}] against {len(list_of_test_files)} files')
        # input("Do you want to continue?")
        try:
            test_availability = row[static_data.cdd_to_cts_app_header.index(static_data.TEST_AVAILABILITY)]
            search_info[TEST_AVAILABILITY] = test_availability
            if test_availability and len(test_availability) > 0:
                print(
                    f" NOTE: Test mapping complete = [{test_availability}] skipping {str(search_info.get(FULL_KEY))}] for [{search_info.get(SEARCH_TERMS)}] ")
                return search_info
        except:
            pass
        self.match_count = 0
        self.is_exact_match = False
        search_dependency_set = set()
        not_found_set = set()
        for file_to_search in list_of_test_files:
            # if there is not filter data OR the filter is match search
            if ((search_root is None) or (len(search_root) == 0)) or (file_to_search.find(search_root) != -1):
                if self.match_count < self.max_matches:
                    self.execute_search_on_file_for_terms_return_results((search_info, file_to_search))
                    search_result: dict = search_info.get(SEARCH_RESULT)
                    if search_result is None or search_result.get(METHOD) is None:
                        not_found_set.add(file_to_search)
                else:
                    skip_count += 1
            if self.is_exact_match:
                break
        search_result = search_info.get(SEARCH_RESULT)
        if search_result is None or search_result.get(METHOD) is None:
            for not_found_in in not_found_set:
                dependency_set: set = self.__dependency_dictionary.get(not_found_in)
                if dependency_set:
                    search_dependency_set.update(dependency_set)
            print(f" Search {len(search_dependency_set)} files")
            for dependency_file in search_dependency_set:
                dependency_file = str(dependency_file)
                if ((not search_root) or (len(search_root) == 0)) or (dependency_file.find(search_root) != -1):
                    if self.match_count < self.max_matches:
                        self.execute_search_on_file_for_terms_return_results((search_info, dependency_file))
                    else:
                        skip_count += 1

        results = search_info.get(SEARCH_RESULT)
        print(f"Search of {search_info.get(SEARCH_TERMS)}")

        if results:
            if logging: print(f"\nresult =[{search_info.get(SEARCH_RESULT)}]\n")
            try:
                matched = sorted(results.get(MATCHED_TERMS).count_value_dict.items(), key=lambda x: x[1], reverse=True)
                if logging: print(f"Matches!  {self.match_count} of {self.max_matches} allowed: matched  {matched}\n")
            except:
                pass
        else:
            print("No matches!")

        if self.match_count > self.max_matches:
            if logging: print(
                f"\nNOTE: SKIPPED {skip_count} files limiting matches to {self.max_matches} skipped many files!!!\n")

        return search_info

    def publish_each_result(self, search_info:dict)->dict:
        if search_info.get(SEARCH_RESULT):
            self.result_subject.on_next(search_info)
        return search_info


def my_print(v: Any, f: Any = '{}') -> Any:
    print(f.format(v))
    return v


def translate_flat(result: dict) -> dict:
    flat_result = dict()
    if not result:
        return flat_result
    flat_result[ROW] = result.get(ROW)
    flat_result[FULL_KEY] = result.get(FULL_KEY)
    flat_result[SECTION_ID] = result.get(SECTION_ID)
    flat_result[REQ_ID] = result.get(REQ_ID)
    flat_result[SEARCH_RESULT] = dict(result.get(SEARCH_RESULT)).get(FLAT_RESULT)
    return flat_result


if __name__ == '__main__':
    start = time.perf_counter()
    rd = RxData()
    rd.max_matches = 200
    result_table = [[str]]

    # input_file_name1= "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/sub1_3_software.csv"
    # output_file_name1 = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output1/results_sub1_3_software.csv"
    # input_file_name = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/FILTERED_TABLE_TO_SEARCH.csv"
    #
    # input_file_name = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/3.2.3.5_input.tsv"
    # output_file_name= "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output/3_2.3.5_output.tsv"
    # output_file_name = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output1/3_2.3.5-c-12-1_out.csv"
    # input_file_name = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/3.2.3.5_input.tsv"
    # output_file_name= "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/output1/3.2.3.5_output.tsv"

    ""
    # input_file_name= static_data.FILTERED_TABLE_TO_SEARCH
    # output_file_name = static_data.RX_WORKING_OUTPUT_TABLE_TO_EDIT
    # #
    # test_output_exists = Path(output_file_name)
    # if test_output_exists.exists():
    #         table_ops.update_manual_fields_from_files(input_file_to_be_updated_with_manual_terms=input_file_name,output_file_to_take_as_input_for_update=output_file_name)
    # input_file_name = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/a1_working/2021-10-11-gpoor-todo_built.tsv"
    current_file = "/a1_working/4.tsv"
    temp_result= current_file+".tmp.tsv"
    final_result= current_file


    rd.result_subject.pipe(
        ops.map(lambda result: translate_flat(result))
        , ops.filter(lambda flat_result: len(flat_result) != 0)
        , ops.map(lambda flat_result: build_row(flat_result, header=static_data.cdd_to_cts_app_header, do_log=True))
        , ops.to_list()
        ,
        ops.map(
            lambda table: table_ops.write_table(current_file + "_flat.tsv", table, static_data.cdd_to_cts_app_header))) \
        .subscribe(on_completed=lambda: print("complete result_subject"),
                   on_error=lambda err: helpers.raise_error("result_subject", err))

    rd.main_do_create_table(current_file, temp_result).subscribe(
        on_next=lambda table: my_print(f"react.py main created [{temp_result}] from [{current_file}] "),
        on_completed=lambda: rd.do_on_complete(),
        on_error=lambda err: helpers.raise_error("in main", err))
    update_release_table_with_changes(current_file,temp_result,final_result,static_data.results_header)
    # copyfile(static_data.WORKING_ROOT+output_file_name, static_data.WORKING_ROOT+input_file_name)
    # rx.from_iterable(test_dic).subscribe( lambda value: print("Received {0".format(value)))
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
