import os
import time

import rx
from rx import operators as ops

import class_graph
import sourcecrawlerreducer
from cdd_html_to_cts_create_sheets import read_table, parse_cdd_html_to_requirements, \
    build_test_cases_module_dictionary


def file_transform_to_full_path(value):
    tvalue: [str, [], []] = value
    return rx.from_list(tvalue[2])


cts_files = rx.from_iterable(os.walk(sourcecrawlerreducer.CTS_SOURCE_ROOT))

java_files = cts_files.pipe(
    ops.map(lambda value: file_transform_to_full_path(value))
)


class RequirementSources:
    table, keys_from_table, header = read_table("input/new_recs_remaining_todo.csv")
    key_to_full_requirement_text, key_to_java_objects, key_to_urls, keys_not_found, cdd_string = \
        parse_cdd_html_to_requirements()


class DataSources:
    parse_dependency_file = sourcecrawlerreducer.get_file_dependencies()
    tests_files_methods = class_graph.get_cached_grep_of_at_test_files()
    files_to_test_cases = build_test_cases_module_dictionary('input/testcases-modules.txt')

    files_to_words, method_to_words, files_to_method_calls = sourcecrawlerreducer.SourceCrawlerReducer().get_cached_crawler_data()
    rx_cts_files = rx.from_iterable(os.walk(sourcecrawlerreducer.CTS_SOURCE_ROOT))
    rx_files_to_words = rx.from_iterable(sorted(files_to_words.items(), key=lambda x: x[1], reverse=True))
    rx_method_to_words = rx.from_iterable(sorted(method_to_words.items(), key=lambda x: x[1], reverse=True))
    rx_files_to_method_calls = rx.from_iterable(sorted(files_to_method_calls.items(), key=lambda x: x[1], reverse=True))


def my_print(v, f: str = '{}'):
    print(f.format(v))


if __name__ == '__main__':
    start = time.perf_counter()
    ds = DataSources()
    ds.rx_files_to_words.subscribe(lambda v: my_print(v, "f to w = {}"))
    end = time.perf_counter()
    print(f'Took time {end - start:0.4f}sec ')
