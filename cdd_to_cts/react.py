import os
import re
import time

import rx
from rx import operators as ops
from rx.subject import ReplaySubject

#from cdd_to_cts.check_sheet import ReadSpreadSheet
from cdd_to_cts import static_data_holder
from cdd_to_cts.class_graph import get_cts_root, parse_

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

    def build_replay_of_at_test_files(self, results_grep_at_test: str = "input/test-files.txt"):
        # test_files_to_methods: {str: str} = dict()
        re_annotations = re.compile('@Test.*?$')

        self.replay_at_test_files_to_methods = ReplaySubject(9999)
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
                    test_annotated_file_name = get_cts_root(test_annotated_file_name_absolute_path)
                    # requirement = result.group(0)
                    line_method = file_content.pop()
                    count += 1
                    class_def, method = parse_(line_method)
                    if class_def == "" and method == "":
                        line_method = file_content.pop()
                        count += 1
                        class_def, method = parse_(line_method)
                    if method:
                        self.replay_at_test_files_to_methods.on_next('{} :{}'.format(test_annotated_file_name_absolute_path,method.strip(' ') ))

            self.replay_at_test_files_to_methods.on_completed()

# rx_search_results = rx.pip(ops.)

def my_print(v, f: str = '{}'):
    print(f.format(v))
    return v


def test_rx_files_to_words():
    rd = RxData()
    rd.rx_files_to_words.subscribe(lambda v: my_print(v, "f to w = {}"))


def test_rx_dictionary():
    rd = RxData()
    #rs = ReadSpreadSheet()
    result = dict()
    # rd.rx_at_test_files_to_methods.subscribe(lambda v: my_print(v, "f to w = {}"))
    rd.rx_at_test_files_to_methods.subscribe(lambda value: print("Received {0".format(value)))


def test_rx_at_test_methods():
    rd = RxData()
    rd.build_replay_of_at_test_files()
    # rd.rx_at_test_files_to_methods.subscribe(lambda v: my_print(v, "f to w = {}"))
    rd.replay_at_test_files_to_methods.subscribe(lambda value: print("Received {0}".format(value)))
    pipe_test_file_dot_method= rd.replay_at_test_files_to_methods.pipe(ops.sum(lambda v: 1 ),ops.map(lambda v: my_print(v)))
    filter_file_name = "cts/PaintTest.java"
    pipe_methods_for_file =   rd.replay_at_test_files_to_methods.pipe(ops.filter(lambda v: v.find(filter_file_name)>-1 ))
    at_file_full_path = rd.replay_at_test_files_to_methods.pipe(ops.map(lambda v: str(v).split(" :")[0]),
                                            ops.distinct_until_changed(),ops.map(lambda v: my_print(v)))
    at_file_full_path.subscribe(on_next=lambda value: print("Received3 {0}".format(value)))
    pipe_methods_for_file.subscribe(lambda value: print("Received4 {0}".format(value)))


if __name__ == '__main__':
    start = time.perf_counter()
    test_rx_at_test_methods()

    # rx.pipe () scribe(rx.from_iterable(data_sources.get_cached_grep_of_at_test_files))
    # rx.from_iterable(test_dic).subscribe( lambda value: print("Received {0".format(value)))
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
