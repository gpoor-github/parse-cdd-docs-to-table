import csv
import re
import sys
import time
from typing import Any

import rx
from rx import operators as ops
from rx.subject import ReplaySubject, BehaviorSubject

from cdd_to_cts import helpers, static_data, table_ops
from cdd_to_cts.class_graph import parse_
from cdd_to_cts.helpers import find_java_objects
from cdd_to_cts.static_data import FULL_KEY_RE_WITH_ANCHOR, SECTION_ID_RE_STR


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
        section = key_to_section_split[1]
        req_id_splits = re.split('(?={})'.format(static_data.full_key_string_for_re), section)
        if req_id_splits and len(req_id_splits) > 1:
            return rx.for_in(req_id_splits, find_full_key_callable)
        else:
            req_id_splits = re.split(static_data.composite_key_string_re, str(section))
            if req_id_splits and len(req_id_splits) > 1:
                return rx.from_list(list_map(section_id, req_id_splits))  # build_composite_key_callable).pipe()
    except Exception as exception_process:
        SystemExit(f" process_section {exception_process}")
    return rx.empty()


class RxData:
    # rx_cts_files = rx.from_iterable(os.walk(CTS_SOURCE_ROOT))
    # rx_files_to_words = rx.from_iterable(sorted(files_to_words.items(), key=lambda x: x[1], reverse=True))
    # rx_method_to_words = rx.from_iterable(sorted(method_to_words.items(), key=lambda x: x[1], reverse=True))
    # rx_files_to_method_calls = rx.from_iterable(sorted(files_to_method_calls.items(), key=lambda x: x[1], reverse=True))
    # rx_at_test_files_to_methods = rx.from_iterable(
    #     sorted(at_test_files_to_methods.items(), key=lambda x: x[1], reverse=True))

    def __init__(self):
        self.__input_table = None
        self.__input_header = None
        self.__input_table_keys = None

        self.result_subject = BehaviorSubject("0:" + str(static_data.new_header))
        self.__replay_input_table = None

        self.__replay_header = None
        self.__replay_at_test_files_to_methods = None
        self.__replay_cdd_requirements = None

    def get_input_table(self, table_dict_file=static_data.INPUT_TABLE_FILE_NAME):
        # input_table, input_table_keys_to_index, input_header, duplicate_rows =
        if not self.__input_header:
            self.__input_table, self.__input_table_keys, self.__input_header, duplicate_row = table_ops.read_table(
                table_dict_file)
        return self.__input_table, self.__input_table_keys, self.__input_header

    def get_manual_search_terms(self, key: str, manual_search_terms="../manual/manual.csv"):
        table, key_fields, header = self.get_input_table(manual_search_terms)
        row = table[key_fields[key]]
        mst_idx = header.index("manual_search_terms")
        manual_search_terms = row[mst_idx]
        return set(manual_search_terms.split(' '))

    def predicate(self, target) -> bool:
        # print("predicate " + str(target))
        result = self.find_search_result(target)
        if result:
            self.result_subject.on_next(result)
            return True
        return False

    def find_search_result(self, target) -> Any:
        # print("predicate " + str(target))
        result_dict = None
        terms = str(target[0]).split(' ')
        result = None
        thing_to_search = helpers.read_file_to_string(target[1])
        for term in terms:
            term.strip(')')
            si = thing_to_search.find(term)
            is_found = si > 1
            if is_found:
                for method_text in thing_to_search.split("@Test"):
                    mi = method_text.find(term)
                    if mi > -1:
                        method_text = method_text.replace('\n',' ')
                        result_dict = dict()
                        result_dict['target'] = target
                        result_dict['match'] = [term,mi,method_text]
                        result = f'["{term}",["{mi}":"{method_text}"]]'
                        print(f"\nmatched: {result}")
                result_dict

        return result_dict

    def get_replay_of_at_test_files_only(self,
                                         results_grep_at_test: str = (
                                                 "%s" % static_data.TEST_FILES_TXT)) -> rx.Observable:

        return self.get_replay_of_at_test_files(results_grep_at_test).pipe(
            ops.map(lambda target: target.split(' :')[0]), ops.distinct())

    def get_replay_of_at_test_files(self,
                                    results_grep_at_test: str = ("%s" % static_data.TEST_FILES_TXT)) -> ReplaySubject:

        if self.__replay_at_test_files_to_methods:
            print(
                f"Warning get_replay_of_at_test_files() ignoring input file {results_grep_at_test} in to use cashed data")
            return self.__replay_at_test_files_to_methods
        else:
            self.__replay_at_test_files_to_methods = ReplaySubject(9999)

        re_annotations = re.compile('@Test.*?$')

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
                    class_def, method = parse_(line_method)
                    if class_def == "" and method == "":
                        line_method = file_content.pop()
                        count += 1
                        class_def, method = parse_(line_method)
                    if method:
                        self.__replay_at_test_files_to_methods.on_next(
                            '{} :{}'.format(test_annotated_file_name_absolute_path, method.strip(' ')))

            self.__replay_at_test_files_to_methods.on_completed()
            return self.__replay_at_test_files_to_methods

    def get_replay_read_table(self, file_name: str = static_data.INPUT_TABLE_FILE_NAME) -> [ReplaySubject,
                                                                                            ReplaySubject]:

        if self.__replay_input_table and self.__replay_header:
            return self.__replay_input_table, self.__replay_header
        else:
            self.__replay_input_table = ReplaySubject(1500)
            self.__replay_header = ReplaySubject(50)

        section_id_index = 1
        req_id_index = 2
        duplicate_rows: [str, str] = dict()

        try:
            with open(file_name) as csv_file:

                csv_reader_instance = csv.reader(csv_file, delimiter=',')
                table_index = 0

                for row in csv_reader_instance:
                    if table_index == 0:
                        try:
                            section_id_index = row.index("section_id")
                            req_id_index = row.index("req_id")
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
            print(f"Failed to open file {file_name} exception -= {type(e)} exiting...")
            sys.exit(f"Fatal Error Failed to open file {file_name}")

    def get_filtered_cdd_by_table(self, input_table_file=static_data.INPUT_TABLE_FILE_NAME,
                                  cdd_requirements_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE, scheduler: rx.typing.Scheduler = None) -> rx.Observable:

        table_dic = observable_to_dict(self.get_replay_read_table(input_table_file)[0])
        return self.get_cdd_html_to_requirements(cdd_requirements_file,scheduler) \
            .pipe(ops.filter(lambda v: table_dic.get(str(v).split(':', 1)[0])))

    def get_cdd_html_to_requirements(self, cdd_html_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE, scheduler: rx.typing.Scheduler = None):

        if not self.__replay_cdd_requirements:
            self.__replay_cdd_requirements = ReplaySubject(buffer_size=2000,scheduler=scheduler)

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
                        self.__replay_cdd_requirements.on_next('{}:{}'.format(cdd_section_id, section))
            self.__replay_cdd_requirements.on_completed()
            # if all ready read, just return it.
        return self.__replay_cdd_requirements.pipe(
            ops.flat_map(lambda section_and_key: process_section(section_and_key)))

    def get_at_test_method_words(self, test_file_grep_results=static_data.TEST_FILES_TXT):
        return self.get_replay_of_at_test_files(test_file_grep_results).pipe(ops.map(lambda v: str(v).split(" :")[0]),
                                                                             ops.distinct_until_changed(),
                                                                             ops.map(lambda f:
                                                                                     f'{f}:{helpers.read_file_to_string(f)}'))

    def find_search_terms(self, requirement_text: str) -> str:
        java_objects = find_java_objects(requirement_text)
        req_split = requirement_text.split(':', 1)
        key_split = req_split[0].split('/')
        java_objects.add(key_split[0])
        if len(key_split) > 1:
            java_objects.add(key_split[1])
        # try:
        #     manual_values = self.get_manual_search_terms(req_split[0])
        #     if manual_values and len(manual_values) > 0:
        #         java_objects.update(manual_values)
        # except:
        #     pass

        return ' '.join(java_objects)

    def get_search_terms(self, get_cdd_html_to_requirements: rx.Observable) -> rx.Observable:
        return get_cdd_html_to_requirements.pipe(
            ops.map(lambda key_requirement_as_text: self.find_search_terms(
                key_requirement_as_text)))

    def test_do_search(self, ):
        return self.get_search_terms(
            self.get_filtered_cdd_by_table(static_data.INPUT_TABLE_FILE_NAME, "input/cdd.html")).pipe(
            ops.combine_latest(self.get_replay_of_at_test_files_only()),
            ops.map(lambda req: self.find_search_result(req)),
            ops.filter(lambda result: result != None))

    def do_search(self, input_table_file=static_data.INPUT_TABLE_FILE_NAME,
                                  cdd_requirements_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE, scheduler: rx.typing.Scheduler = None ):
        return self.get_search_terms(
            self.get_filtered_cdd_by_table(input_table_file, cdd_requirements_file,scheduler).pipe(
            ops.combine_latest(self.get_replay_of_at_test_files_only()),
            ops.map(lambda req: self.find_search_result(req)),
            ops.filter(lambda result: result )))

def my_print(v, f: str = '{}'):
    print(f.format(v))
    return v


if __name__ == '__main__':
    start = time.perf_counter()
    rd = RxData()
    rd.do_search().subscribe(on_next=lambda value: print("Received {0}".format(value)),
                             on_completed=lambda: print("completed"),
                             on_error=lambda err2: print("error {0}".format(err2)))

    # rx.from_iterable(test_dic).subscribe( lambda value: print("Received {0".format(value)))
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
