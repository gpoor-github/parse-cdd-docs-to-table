#  Block to comment
import os
import unittest
import time
import unittest
from typing import Any

import rx
from rx import operators as ops, pipe
from rx.testing import TestScheduler, ReactiveTest

import data_sources
from cdd_to_cts import static_data, parser_helpers, react, table_ops
from cdd_to_cts.react import RxData, build_row, build_dict, \
    created_and_populated_search_info_from_key_row_tuple, my_print
from cdd_to_cts.static_data import SEARCH_TERMS
from parser_constants import HEADER_KEY, SEARCH_RESULT, SECTION_ID, DEFAULT_SECTION_ID_INDEX, FULL_KEY


class BrokenTestsToFixSomeday(unittest.TestCase):

    def test_do_search_unfiltered_on_results(self, ):
        rd = RxData()
        table, header = rd.init_input_table_keyed("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/new_recs_remaining_todo.csv")
        rd.do_search(table, header, ).pipe(
                                           ops.map(lambda req: my_print(req, "test_do_search[{}]")),
                                           ops.count()).subscribe(lambda count: self.assertEqual(count, 1029))

    def test_filtered_cdd_by_table(self, ):
        scheduler = TestScheduler()
        rd = RxData()
        composed = pipe( rd.get_pipe_create_results_table())

        # composed.subscribe()

        def create():
            return composed

        subscribed = 300
        disposed = 1400
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
        print(results.messages)
        self.assertRegexpMatches(str(results.messages), "3.2.3.5/C-4-1")
        self.assertRegexpMatches(str(results.messages), "3.2.3.5/C-6-1")

        print("done")
    # 2264 != 2266

    def test_all_search_terms(self, ):
        rd = RxData()
        header = ['Section', 'section_id', 'req_id', 'Test Availability', 'class_def', 'method', 'module', 'method_text',
         'full_key', 'requirement', 'key_as_number', 'search_terms', 'manual_search_terms', 'not_search_terms',
         'not_files', 'matched_terms', 'search_roots', 'qualified_method', 'max_matches', 'file_name', 'matched_files',
         'methods_string', 'urls', 'protected', 'Area', 'Shortened', 'Test Level']
        key_req = "9.16/C-1-1:] The memory available to the kernel and userspace MUST be at least 1280MB if the default display uses framebuffer resolutions up to FHD (e.g. WSXGA+). </p> </li> <li> <p>"
        expected = {'9.16', 'FHD', 'WSXGA', 'C-1-1'}
        file_to_search = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/EncoderInitializationLatencyTest.java"

        row = ('3/A-1-1', ['3 . Software', '3', 'A-1-1', '', '', '', '', '', '3/A-1-1',
                           '">3/A-1-1] MUST NOT attach special privileges to system application\'s use of these properties; or prevent third-party applications from using these properties. [<a href="#3_0_intro""',
                           '03000000.650101', "{'3', 'A-1-1'}", '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                           ''])

        search_info = created_and_populated_search_info_from_key_row_tuple(row, header)
        # search_info = react.get_search_terms_from_requirements_and_key_create_search_info_dictionary(key_req)
        rd.execute_search_on_file_for_terms_return_results((search_info,file_to_search))
        expected_manual = {'secure', 'screen', 'lock', 'verification'}
        rx.just((search_info,file_to_search)).pipe(
            ops.map(lambda dict_and_file: rd.execute_search_on_file_for_terms_return_results(dict_and_file)),
            ops.map(lambda search_info: created_and_populated_search_info_from_key_row_tuple(search_info,
                                                                                           "test/input/test_manual_search.csv")),
            ops.map(lambda search_info: self.assertEqual(expected_manual,
                                                         search_info.get(
                                                             static_data.MANUAL_SEARCH_TERMS)))).subscribe(
            lambda search_info: self.assertEqual(expected_manual, search_info.get(static_data.SEARCH_TERMS)))

    #
    # def test_search(self, ):
    #     rd = RxData()
    #     rd.created_and_populated_search_info_from_key_row_tuple(
    #         rd.get_filtered_cdd_by_table("input/new_recs_remaining_todo.csv", "input/cdd.html")).pipe(
    #         ops.map(lambda req: my_print(req, "find_search_terms[{}]")),
    #         ops.combine_latest(rd.get_replay_of_at_test_files_only()),
    #
    #         ops.filter(lambda result: dict(result).get("dictionary_with_existing_values")),
    #         ops.map(lambda req: my_print(req, "find_search_result[{}]")),
    #
    #         ops.map(lambda v: my_print2(v, "find_downstream_search_result[{}]")),
    #         ops.count()).subscribe(lambda count: self.assertEqual(count, 32))

    def test_do_search(self, ):
        rd = RxData()
        table, header = rd.init_input_table_keyed("/input/four_line_created.csv")
        rd.do_search(table, header).pipe(
            ops.filter(lambda result: dict(result).get("dictionary_with_existing_values")),
            ops.map(lambda req: my_print(req, "test_do_search[{}]")),
            ops.count()).subscribe(lambda count: self.assertEqual(950,count ))


    def test_handle_search_results_debug(self, ):
        scheduler = TestScheduler()
        rd = RxData()
        table, header = rd.init_input_table_keyed("../input/four_line_created.csv")

        composed = rd.do_search(table, header, scheduler=scheduler)

        # composed.subscribe()

        def create():
            return composed

        subscribed = 300
        disposed = 1400
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
        print(results.messages)
        self.assertRegexpMatches(str(results.messages), "3/A-1-1")

        print("done")

    def test_get_input_table_keyed(self, ):
        scheduler = TestScheduler()
        header = ["Section", "section_id", "req_id", "full_key", "requirement", "manual_search_terms"]
        rd = RxData()

        table_dict, header = rd.init_input_table_keyed("input/input_table_key_index_mod.csv")
        pipe = rx.from_iterable(table_dict, scheduler).pipe(ops.map(lambda key: (key, table_dict.get(key))),
                                                            ops.map(lambda tdict: my_print(tdict,
                                                                                           "test test_table_dict[{}]\n")))

        # .subscribe(lambda key, row: self.assertTupleEqual())

        def create():
            return pipe

        subscribed = 300
        disposed = 1800
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
        print(results.messages)
        #        self.assertCountEqual("Section,section_id,req_id,requirement".split(','), dict(table_dict).get(HEADER_KEY))

        t0 = (0, ['Section', 'section_id', 'req_id', 'requirement'])
        r1 = ",3.2.3.5,C-4-1,req-c-4-1".split(',')
        r2 = ",3.2.3.5,C-5-1,req-c-5-1".split(',')
        r3 = ",3.2.3.5,C-5-2,req-c-5-2".split(',')
        r4 = ",3.2.3.5,C-6-1,req-c-6-1".split(',')
        k1 = "3.2.3.5/C-4-1"
        k2 = "3.2.3.5/C-5-1"
        k3 = "3.2.3.5/C-5-2"
        k4 = "3.2.3.5/C-6-1"

        assert results.messages == [
            ReactiveTest.on_next(300, (HEADER_KEY, table_dict.get(HEADER_KEY))),
            ReactiveTest.on_next(300, (k1, r1)),
            ReactiveTest.on_next(300, (k2, r2)),
            ReactiveTest.on_next(300, (k3, r3)),
            ReactiveTest.on_next(300, (k4, r4)),
            ReactiveTest.on_completed(300)
        ]


    def test_auto_search_terms(self, ):
        key_req = "2.2.1/H-7-11:] The memory available to the kernel and userspace MUST be at least 1280MB if the default display uses framebuffer resolutions up to FHD (e.g. WSXGA+). </p> </li> <li> <p>"
        expected = {'2.2.1', 'FHD', 'WSXGA', 'H-7-11'}
        key_req2 = "    <li>[<a href=""https://source.android.com/compatibility/11/android-11-cdd#3_0_intro"">3</a>/W-0-1] MUST declare the"
        header = ['Section', 'section_id', 'req_id',  'requirement','Test Availability', 'class_def', 'method', 'module',
                  'method_text', 'full_key', 'requirement', 'key_as_number', 'search_terms', 'manual_search_terms',
                  'not_search_terms', 'not_files', 'matched_terms', 'search_roots', 'qualified_method', 'max_matches',
                  'file_name', 'matched_files', 'methods_string', 'urls', 'protected', 'Area', 'Shortened',
                  'Test Level']
        row = ('3/A-1-1', ['3 . Software', '3', 'A-1-1', '">3/A-1-1] MUST NOT attach special privileges to system application\'s use of these properties; or prevent third-party applications from using these properties. [<a href="#3_0_intro""',
                           '03000000.650101', "{'3', 'A-1-1'}", '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                           ''])

        search_info = react.created_and_populated_search_info_from_key_row_tuple(row, header)

        key_req2 = "    <li>[<a href=""https://source.android.com/compatibility/11/android-11-cdd#3_0_intro"">3</a>/W-0-1] MUST declare the"
        key_req2 = parser_helpers.cleanhtml(key_req2)
        rd = RxData()
        self.assertEqual(expected,
                         search_info.get( SEARCH_TERMS))
        self.assertEqual("2.2.1/H-7-11", search_info.get(FULL_KEY))



if __name__ == '__main__':
    unittest.main()
