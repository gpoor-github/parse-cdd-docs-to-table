import csv
import re
import sys
import time

import rx
from rx import operators as ops
from rx.subject import ReplaySubject

import static_data
from cdd_to_cts import helpers
from cdd_to_cts.class_graph import parse_
from cdd_to_cts.static_data import FULL_KEY_RE_WITH_ANCHOR, SECTION_ID_RE_STR


def file_transform_to_full_path(value):
    tvalue: [str, [], []] = value
    return rx.from_list(tvalue[2])


def read_file_to_string(file):
    with open(file, "r") as text_file:
        file_string_raw = text_file.read()
        file_string = re.sub(' Copyright.+limitations under the License', "", file_string_raw, flags=re.DOTALL)
        text_file.close()
        return file_string


def find_full_key_callable(record_id_split: [[int], str]) -> str:
    record_id_result = re.search(FULL_KEY_RE_WITH_ANCHOR, record_id_split)
    if record_id_result:
        record_id_string = record_id_result[0]
        record_id_string = record_id_string.replace("</a>", "")
        return rx.just("{}:{}".format(record_id_string.rstrip(']').lstrip('>'),record_id_split))
    return rx.just("")


def list_map(section_id: str, record_splits: list) -> list:
    # mysubject = ReplaySubject()
    dict_list = list()
    for record_split in record_splits:
        record_id = ""
        test_section_id = helpers.find_section_id(record_split)
        if test_section_id and len(test_section_id) > 0:
            section_id = test_section_id
        record_id_result = re.search(static_data.req_id_re_str, record_split)
        if record_id_result and record_id_result[0]:
            record_id = record_id_result[0].rstrip(']')
            dict_list.append('{}/{}:{}'.format(section_id, record_id,record_split))

    return dict_list


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
                return rx.from_list(list_map(section_id,req_id_splits))# build_composite_key_callable).pipe()
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

    replay_at_test_files_to_methods: ReplaySubject

    def __init__(self):
        self.replay_input_table = ReplaySubject(9999)
        self.replay_header = ReplaySubject(1)
        self.replay_at_test_files_to_methods = ReplaySubject(9999)
        self.replay_cdd_requirements = ReplaySubject(2000)

    def build_replay_of_at_test_files(self, results_grep_at_test: str = ("%s" % static_data.TEST_FILES_TXT)):
        # test_files_to_methods: {str: str} = dict()
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
                    line_method = file_content.pop()
                    count += 1
                    class_def, method = parse_(line_method)
                    if class_def == "" and method == "":
                        line_method = file_content.pop()
                        count += 1
                        class_def, method = parse_(line_method)
                    if method:
                        self.replay_at_test_files_to_methods.on_next(
                            '{} :{}'.format(test_annotated_file_name_absolute_path, method.strip(' ')))

            self.replay_at_test_files_to_methods.on_completed()

    def build_replay_read_table(self, file_name: str):

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
                            self.replay_header.on_next(row)
                            self.replay_header.on_completed()
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

                    self.replay_input_table.on_next(f'{key_value}:{row}')

                if len(duplicate_rows) > 0:
                    print(
                        f"ERROR, reading tables with duplicate 1 {file_name} has={len(duplicate_rows)} duplicates {duplicate_rows} ")
                else:
                    duplicate_rows = None
            self.replay_input_table.on_completed()

            return self.replay_input_table, self.replay_header
        except IOError as e:
            print(f"Failed to open file {file_name} exception -= {type(e)} exiting...")
            sys.exit(f"Fatal Error Failed to open file {file_name}")

    def build_rx_parse_cdd_html_to_requirements(self, cdd_html_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE):

        with open(cdd_html_file, "r") as text_file:
            cdd_requirements_file_as_string = text_file.read()
            section_id_re_str: str = SECTION_ID_RE_STR
            cdd_sections_splits = re.split('(?={})'.format(section_id_re_str), cdd_requirements_file_as_string,
                                           flags=re.DOTALL)
            section_id_count = 0
            for section in cdd_sections_splits:
                cdd_section_id = helpers.find_section_id(section)
                if cdd_section_id:
                    if '13' == cdd_section_id:
                        # section 13 is "Contact us" and has characters that cause issues at lest for git
                        print(f"Warning skipping section 13 {section}")
                        continue
                    section = re.sub('\s\s+', ' ', section)
                    self.replay_cdd_requirements.on_next('{}:{}'.format(cdd_section_id, section))
        self.replay_cdd_requirements.on_completed()
        return self.replay_cdd_requirements


def my_print(v, f: str = '{}'):
    print(f.format(v))
    return v


def test_rx_files_to_words():
    rd = RxData()
    rd.replay_at_test_files_to_methods.subscribe(lambda v: my_print(v, "f to w = {}"))


def test_rx_dictionary():
    rd = RxData()
    # rs = ReadSpreadSheet()
    # rd.rx_at_test_files_to_methods.subscribe(lambda v: my_print(v, "f to w = {}"))
    rd.replay_at_test_files_to_methods.subscribe(lambda value: print("Received {0".format(value)))


def test_rx_at_test_methods():
    rd = RxData()
    rd.build_replay_of_at_test_files()
    # rd.rx_at_test_files_to_methods.subscribe(lambda v: my_print(v, "f to w = {}"))
    rd.replay_at_test_files_to_methods.subscribe(lambda value: print("Received {0}".format(value)))
    pipe_test_file_dot_method = rd.replay_at_test_files_to_methods.pipe(ops.sum(lambda v: 1),
                                                                        ops.map(lambda v: my_print(v)))
    filter_file_name = "cts/PaintTest.java"
    pipe_methods_for_file = rd.replay_at_test_files_to_methods.pipe(ops.filter(lambda v: v.find(filter_file_name) > -1))
    at_file_full_path = rd.replay_at_test_files_to_methods.pipe(ops.map(lambda v: str(v).split(" :")[0]),
                                                                ops.distinct_until_changed(),
                                                                ops.map(lambda v: my_print(v)))
    pipe_words_for_file = at_file_full_path.pipe(ops.map(lambda f: f'{f}:{read_file_to_string(f)}'))
    return pipe_words_for_file


def test_rx_table():
    rd = RxData()
    rd.replay_header.subscribe(lambda v: my_print(v, "header = {}"))
    rd.replay_input_table.subscribe(lambda v: my_print(v, "table = {}"))

    rd.build_replay_read_table(static_data.INPUT_TABLE_FILE_NAME)
    print("done")


def test_rx_cdd_read():
    rd = RxData()
    # rd.replay_cdd_requirements.subscribe(lambda v: my_print(v, "cdd = {}"))
    rd.build_rx_parse_cdd_html_to_requirements(static_data.CDD_REQUIREMENTS_FROM_HTML_FILE)
    return rd.replay_cdd_requirements.pipe(ops.take(1535),ops.flat_map(lambda section_and_key: process_section(section_and_key)),
                                           ops.map(lambda req: my_print(req, 'req[{}]\n')),
                                           ops.count(lambda v: True))

if __name__ == '__main__':
    start = time.perf_counter()
    test_rx_cdd_read().subscribe(on_next=lambda value: print("Received {0}".format(value)),
                                 on_completed=lambda: print("completed"),
                                 on_error=lambda err2: print("error {0}".format(err2)))

    # rx.from_iterable(test_dic).subscribe( lambda value: print("Received {0".format(value)))
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
