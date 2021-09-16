import csv
import re
import sys
import time

import rx
from rx import operators as ops
from rx.subject import ReplaySubject

# from cdd_to_cts.check_sheet import ReadSpreadSheet
from cdd_to_cts import static_data_holder
from cdd_to_cts.class_graph import parse_
from cdd_to_cts.static_data_holder import TEST_FILES_TXT, CDD_REQUIREMENTS_FROM_HTML_FILE


def file_transform_to_full_path(value):
    tvalue: [str, [], []] = value
    return rx.from_list(tvalue[2])


def read_file_to_string(file):
    with open(file, "r") as text_file:
        file_string_raw = text_file.read()
        file_string = re.sub(' Copyright.+limitations under the License', "", file_string_raw, flags=re.DOTALL)
        text_file.close()
        return file_string


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

    def build_replay_of_at_test_files(self, results_grep_at_test: str = ("%s" % TEST_FILES_TXT)):
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


    def build_rx_parse_cdd_html_to_requirements(self, cdd_html_file=CDD_REQUIREMENTS_FROM_HTML_FILE):

        with open(cdd_html_file, "r") as text_file:
            cdd_requirements_file_as_string = text_file.read()
            section_id_re_str: str = '"(?:\d{1,3}_)+'
            cdd_sections_splits = re.split('(?={})'.format(section_id_re_str), cdd_requirements_file_as_string,
                                           flags=re.DOTALL)
            section_id_count = 0
            for section in cdd_sections_splits:
                cdd_section_id_search_results = re.search(section_id_re_str, section)
                if not cdd_section_id_search_results:
                    continue

                cdd_section_id = cdd_section_id_search_results[0]
                cdd_section_id = cdd_section_id.replace('"', '').rstrip('_')
                cdd_section_id = cdd_section_id.replace('_', '.')
                #
                if '13' == cdd_section_id:
                    # section 13 is "Contact us" and has characters that cause issues at lest for git
                    print(f"Warning skipping section 13 {section}")
                    continue
            self.replay_cdd_requirements.on_next('{}:{}'.format(cdd_section_id, section))
        self.replay_cdd_requirements.on_completed()
        return self.replay_cdd_requirements

    def process_section(self, record_key_method, key_string_for_re, section_id, key_to_full_requirement_text_param,
                    record_id_splits, section_id_count, total_requirement_count):
        record_id_count = 0

        for record_id_split in record_id_splits:
            key = record_key_method(key_string_for_re, record_id_split, section_id)
            if key:
                from cdd_to_cts.data_sources import clean_html_anchors
                record_id_split = clean_html_anchors(record_id_split)
                record_id_count += 1
                total_requirement_count += 1
                print(
                    f'key [{key}] {key_string_for_re} value [{key_to_full_requirement_text_param.get(key)}] section/rec_id_count {section_id_count}/{record_id_count} {total_requirement_count} ')
                from cdd_to_cts import data_sources
                key_to_full_requirement_text_param[key] = data_sources.process_requirement_text(record_id_split,
                                                                                   key_to_full_requirement_text_param.get(
                                                                                       key))
        return total_requirement_count

def my_print(v, f: str = '{}'):
    print(f.format(v))
    return v


def test_rx_files_to_words():
    rd = RxData()
    rd.replay_at_test_files_to_methods.subscribe(lambda v: my_print(v, "f to w = {}"))


def test_rx_dictionary():
    rd = RxData()
    # rs = ReadSpreadSheet()
    result = dict()
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

    rd.build_replay_read_table(static_data_holder.INPUT_TABLE_FILE_NAME)
    print("done")


def test_rx_cdd_read():
    rd = RxData()
    rd.replay_cdd_requirements.subscribe(lambda v: my_print(v, "cdd = {}"))
    rd.build_rx_parse_cdd_html_to_requirements(static_data_holder.CDD_REQUIREMENTS_FROM_HTML_FILE)
    return rd.replay_cdd_requirements


if __name__ == '__main__':
    start = time.perf_counter()
    test_rx_cdd_read().subscribe(lambda value: print("Received4 {0}".format(value)))

    # rx.pipe () scribe(rx.from_iterable(data_sources.get_cached_grep_of_at_test_files))
    # rx.from_iterable(test_dic).subscribe( lambda value: print("Received {0".format(value)))
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
