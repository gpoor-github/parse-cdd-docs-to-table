import os
import time

import rx
from rx import operators as ops

from cdd_to_cts import check_sheet
from cdd_to_cts.check_sheet import ReadSpreadSheet
from cdd_to_cts.static_data_holder import CTS_SOURCE_PARENT
from data_sources import CTS_SOURCE_ROOT, files_to_words, method_to_words, files_to_method_calls, \
    at_test_files_to_methods


def file_transform_to_full_path(value):
    tvalue: [str, [], []] = value
    return rx.from_list(tvalue[2])


cts_files = rx.from_iterable(os.walk(CTS_SOURCE_ROOT))

java_files = cts_files.pipe(
    ops.map(lambda value: file_transform_to_full_path(value))
)


class RxData:
    rx_cts_files = rx.from_iterable(os.walk(CTS_SOURCE_ROOT))
    rx_files_to_words = rx.from_iterable(sorted(files_to_words.items(), key=lambda x: x[1], reverse=True))
    rx_method_to_words = rx.from_iterable(sorted(method_to_words.items(), key=lambda x: x[1], reverse=True))
    rx_files_to_method_calls = rx.from_iterable(sorted(files_to_method_calls.items(), key=lambda x: x[1], reverse=True))
    rx_at_test_files_to_methods = rx.from_iterable(
        sorted(at_test_files_to_methods.items(), key=lambda x: x[1], reverse=True))






















# rx_search_results = rx.pip(ops.)

def my_print(v, f: str = '{}'):
    print(f.format(v))
    return v


def test_rx_files_to_words():
    rd = RxData()
    rd.rx_files_to_words.subscribe(lambda v: my_print(v, "f to w = {}"))


def test_rx_at_test_methods():
    rd = RxData()
    rs = ReadSpreadSheet()
    result = dict()
    # rd.rx_at_test_files_to_methods.subscribe(lambda v: my_print(v, "f to w = {}"))
    rd.rx_at_test_files_to_methods.subscribe(lambda value: print("Received {0".format(value)))
    if __name__ == '__main__':
        start = time.perf_counter()
        test_rx_files_to_words()
        end = time.perf_counter()
        print(f'Took time {end - start:0.4f}sec ')
