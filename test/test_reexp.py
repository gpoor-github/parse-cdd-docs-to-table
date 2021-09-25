import time
import unittest
from typing import Any

import rx
from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

from cdd_to_cts import static_data, helpers, react, table_ops
from cdd_to_cts.react import RxData, build_row, SEARCH_RESULT, build_dict, \
    get_search_terms_from_key_create_result_dictionary
from cdd_to_cts.static_data import SEARCH_TERMS, FULL_KEY, HEADER_KEY, SECTION_ID, DEFAULT_SECTION_ID_INDEX


def my_print(v: Any, f: Any = '{}'):
    print(f.format(v))
    return v


def my_print2(v: Any, f: Any = '{}'):
    print(f.format(v))
    return v


def predicate3(target) -> bool:
    print("predicate 3 " + str(target))

    return True


def predicate2(target, source) -> bool:
    print("predicate 2 " + str(target))
    file_name = target.split(" :")[0]
    thing_to_search = helpers.read_file_to_string(file_name)
    is_found = False
    isMatch = rx.Observable(source).pipe(ops.find(predicate=predicate3)).run()

    return isMatch


def my_map_dict(key: str, m_list: list) -> list:
    # mysubject = ReplaySubject()
    dict_list = list()
    for item in m_list:
        if ord(item[0]) > ord("a"):
            key = item
        else:
            dict_list.append("[{}:{}]".format(key, item))
    return dict_list


def test_get_replay_of_at_test_files():
    rd = RxData()
    rd.get_replay_of_at_test_files().subscribe()


class MyTestCase(unittest.TestCase):

    def test_cdd_html_to_requirements(self, ):
        RxData().get_cdd_html_to_requirements("../input/cdd.html").pipe(
            ops.map(lambda v: my_print(v)),
            ops.count(),
            ops.map(lambda count: my_print(count, "count ={}"))). \
            subscribe(lambda count: self.assertEqual(count, 1317))

    def test_filtered_cdd_by_table(self, ):
        scheduler = TestScheduler()
        rd = RxData()
        composed = rd.get_filtered_cdd_by_table("./input/four_line_sparse.csv", "./input/short_cdd_html_3-2-4-5.html",
                                                scheduler=scheduler)

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

    def test_rx_at_test_methods_to_words(self, ):
        RxData().get_at_test_method_words(static_data.TEST_FILES_TXT). \
            pipe(ops.map(lambda v: my_print(v)),
                 ops.count()). \
            subscribe(lambda count: self.assertEqual(count, 964))

    def test_get_cdd_html_to_requirements(self, ):
        rd = RxData()
        rd.get_cdd_html_to_requirements(static_data.CDD_REQUIREMENTS_FROM_HTML_FILE) \
            .pipe(ops.map(lambda v: my_print(v)),
                  ops.count()). \
            subscribe(lambda count: self.assertEqual(count, 1317))

    def test_get_cdd_html_to_requirements_values(self, ):
        rd = RxData()
        a_7_line_table = "../test/input/section_id_length_one_issue.html"

        rd.get_cdd_html_to_requirements(a_7_line_table)

    def test_parse_cdd_html_to_requirements(self, ):
        a_7_line_table = "../test/input/just_one_section_id_digit_issue.html"

        from cdd_to_cts.data_sources_helper import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local, key_to_java_objects_local, key_to_urls_local, cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(
            a_7_line_table)
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-2"))
        self.assertEqual(4, len(key_to_full_requirement_text_local))

    def test_get_cdd_html_to_requirements_table(self, ):
        a_7_line_table = "test/input/section_id_length_one_issue.html"

        rd = RxData()
        rd.cdd_html_to_requirements_csv(a_7_line_table). \
            subscribe(lambda table_dict: self.assertEqual('3', table_dict[2][DEFAULT_SECTION_ID_INDEX]))
        # table_ops.write_table("output/try_table1.csv", table, header=static_data.cdd_to_cts_app_header)
        # my_print2(table_dict) write_table("output/try_table1.csv", table_dict, static_data.cdd_to_cts_app_header)

    def test_get_cdd_html_to_requirements_dict(self, ):
        rd = RxData()
        # table_dict:dict
        rd.get_cdd_html_to_requirements(static_data.CDD_REQUIREMENTS_FROM_HTML_FILE) \
            .pipe(ops.filter(lambda wv: not wv or len(str(wv).split(':')) < 2), ops.map(lambda v: my_print(v)),
                  ops.to_dict(key_mapper=lambda key_req: key_req.split(':')[0],
                              element_mapper=lambda key_req: build_dict(key_req)),
                              ops.map(  lambda tdict: react.write_table_from_dictionary(tdict,"output/tdict.csv")),
                  ops.map(lambda v: my_print2(v))).subscribe(
            lambda table_dict: self.assertEqual(1317, len(dict(table_dict).keys())))

    # Callable[[TState, T1], TState]
    @staticmethod
    def reduce_find(term, target):
        print(f"{term} {target}")
        return target.split(":")[0]

    def does_match(self, target: str, search_terms: rx.Observable) -> rx.Observable:
        return search_terms.pipe(ops.reduce(lambda term: self.reduce_find(term, target)))
        # return search_terms.pipe(ops.find(lambda item: self.does_match_item(target,search_terms)))

    match = False

    def does_match_item(self, target: str, o_term: rx.Observable) -> bool:
        # val = term.lock
        val = True
        o_term.pipe(ops.map(lambda v: my_print(v, "a{}")), ops.to_list(), ops.map(lambda v: my_print(v, "b{}")),
                    ops.filter(lambda term: RxData().predicate(term)), ops.flat_map(rx.just(False)))
        return self.match
        # term = o_term.pipe(ops.first(),o

        # if target.find(term) > -1:
        #     print(f"does_match_item term {term}")
        #     return rx.just(target)
        # else:
        #     return rx.empty()

    # def test_rx_find(self, ):
    #     rd = RxData()
    #     rd.get_replay_of_at_test_files().pipe(ops.find(predicate2)).subscribe()

    def test_replay_simple_at_test_file_only(self, ):
        start = time.perf_counter()
        rd = RxData()
        for i in range(0, 2):
            rd.get_replay_of_at_test_files_only().pipe(ops.count()).subscribe(
                on_next=lambda result: my_print(result, "test_replay_simple_at_test_file_only  ={}"))
        end = time.perf_counter()
        print(f"Took time {end - start:0.4f}sec ")

    def test_manual_search_terms(self, ):
        rd = RxData()
        search_info_in = dict()
        search_info_in['full_key'] = '9.16/C-1-1'
        expected = {'secure', 'screen', 'lock', 'verification'}
        search_info = get_search_terms_from_key_create_result_dictionary(search_info_in,
                                                                         "test/input/test_manual_search.csv")
        self.assertEqual(expected, search_info.get(static_data.MANUAL_SEARCH_TERMS))

    def test_manual_search_terms_bad_key(self, ):
        rd = RxData()
        search_info_in = dict()
        search_info_in['full_key'] = '99.16/x-1-1'
        search_info = get_search_terms_from_key_create_result_dictionary(search_info_in,
                                                                         "test/input/test_manual_search.csv")
        self.assertEqual(None, search_info.get(static_data.MANUAL_SEARCH_TERMS))

    def test_auto_search_terms(self, ):
        key_req = "2.2.1/H-7-11:] The memory available to the kernel and userspace MUST be at least 1280MB if the default display uses framebuffer resolutions up to FHD (e.g. WSXGA+). </p> </li> <li> <p>"
        expected = {'2.2.1', 'FHD', 'WSXGA', 'H-7-11'}
        key_req2 = "    <li>[<a href=""https://source.android.com/compatibility/11/android-11-cdd#3_0_intro"">3</a>/W-0-1] MUST declare the"
        search_info = react.get_search_terms_from_requirements_and_key_create_result_dictionary(key_req)

        key_req2 = "    <li>[<a href=""https://source.android.com/compatibility/11/android-11-cdd#3_0_intro"">3</a>/W-0-1] MUST declare the"
        key_req2 = helpers.cleanhtml(key_req2)
        self.assertEqual(expected,
                         react.get_search_terms_from_requirements_and_key_create_result_dictionary(key_req2).get(
                             SEARCH_TERMS))
        self.assertEqual("2.2.1/H-7-11", search_info.get(FULL_KEY))

    def test_all_search_terms(self, ):
        rd = RxData()
        key_req = "9.16/C-1-1:] The memory available to the kernel and userspace MUST be at least 1280MB if the default display uses framebuffer resolutions up to FHD (e.g. WSXGA+). </p> </li> <li> <p>"
        expected = {'9.16', 'FHD', 'WSXGA', 'C-1-1'}
        # search_info = react.get_search_terms_from_requirements_and_key_create_result_dictionary(key_req)
        expected_manual = {'secure', 'screen', 'lock', 'verification'}
        rx.just(key_req).pipe(
            ops.map(lambda req: react.get_search_terms_from_requirements_and_key_create_result_dictionary(key_req)),
            ops.map(lambda search_info: get_search_terms_from_key_create_result_dictionary(search_info,
                                                                                           "test/input/test_manual_search.csv")),
            ops.map(lambda search_info: self.assertEqual(expected_manual,
                                                         search_info.get(
                                                             static_data.MANUAL_SEARCH_TERMS)))).subscribe(
            lambda search_info: self.assertEqual(expected_manual, search_info.get(static_data.SEARCH_TERMS)))

    #
    # def test_search(self, ):
    #     rd = RxData()
    #     rd.get_search_terms_from_key_create_result_dictionary(
    #         rd.get_filtered_cdd_by_table("input/new_recs_remaining_todo.csv", "input/cdd.html")).pipe(
    #         ops.map(lambda req: my_print(req, "find_search_terms[{}]")),
    #         ops.combine_latest(rd.get_replay_of_at_test_files_only()),
    #
    #         ops.filter(lambda result: dict(result).get("a_dict")),
    #         ops.map(lambda req: my_print(req, "find_search_result[{}]")),
    #
    #         ops.map(lambda v: my_print2(v, "find_downstream_search_result[{}]")),
    #         ops.count()).subscribe(lambda count: self.assertEqual(count, 32))

    def test_do_search_unfiltered_on_results(self, ):
        rd = RxData()
        rd.do_search("input/new_recs_remaining_todo.csv").pipe(
            ops.map(lambda req: my_print(req, "test_do_search[{}]")),
            ops.count()).subscribe(lambda count: self.assertEqual(count, 1029))

    def test_do_search(self, ):
        rd = RxData()
        rd.do_search("./input/full_cdd.csv").pipe(
            ops.filter(lambda result: dict(result).get("a_dict")),
            ops.map(lambda req: my_print(req, "test_do_search[{}]")),
            ops.count()).subscribe(lambda count: self.assertEqual(count, 950))

    # 2264 != 2266
    def test_handle_search_results_debug(self, ):
        scheduler = TestScheduler()
        rd = RxData()
        composed = rd.do_search("input/full_cdd.csv", scheduler=scheduler)

        # composed.subscribe()

        def create():
            return composed

        subscribed = 300
        disposed = 1400
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
        print(results.messages)
        self.assertRegexpMatches(str(results.messages), "3.2.3.5/C-4-1")

        print("done")

    def test_handle_search_results_to_csv(self, ):
        scheduler = TestScheduler()
        rd = RxData()

        # .pipe(ops.map(lambda result_dic: react.publish_results(result_dic, static_data.cdd_to_cts_app_header)), ops.to_list(),
        #  ops.reduce(lambda acc, a: accum2(acc, " ".join(a), seed=[])))
        composed = rd.do_search("./input/full_cdd.csv", scheduler=scheduler).pipe(
            ops.map(lambda req: my_print(req, "test_handle_search_results_to_csv[{}]")),

            ops.filter(lambda search_info: dict(search_info).get(SEARCH_RESULT)),
            ops.map(lambda search_info: get_search_terms_from_key_create_result_dictionary(search_info,
                                                                                           "test/input/test_manual_search.csv")),
            ops.map(lambda req: my_print(req, "test_handle_search_results_to_csv[{}]")),
            ops.map(lambda results_local: rd.find_data_for_csv_dict(dict())),
            ops.map(
                lambda search_info: build_row(search_info, header=static_data.cdd_to_cts_app_header, do_log=True)),
            ops.to_list()) \
            # .pipe(ops.multicast(mapper=lambda value:value,subject=rd.result_subject, scheduler=scheduler))

        # composed.subscribe(

        def create():
            return composed

        subscribed = 300
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=None)
        print(results.messages)

        print("done")

    def test_reducer(self, ):
        rx.from_iterable(range(10)).pipe(ops.reduce(lambda acc, a: acc + list(a), seed=[])
                                         ).subscribe(on_next=lambda result: my_write(result, "test_reducer  ={}"))

    def test_reducer2(self, ):
        rx.from_iterable(range(10)).pipe(ops.reduce(lambda acc, a: accum(acc, a), seed=list)
                                         ).subscribe(on_next=lambda result: my_write(result, "test_reducer  ={}"))

    def test_table_dict(self, ):
        scheduler = TestScheduler()
        interval_time = 300
        rd = RxData()
        table_dict: dict = rd.get_input_table_keyed("test/input/four_line_sparse.csv")
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
        self.assertCountEqual("Section,section_id,req_id,requirement".split(','), dict(table_dict).get(HEADER_KEY))

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

    def test_read_table_section_id_one_digit(self, ):
        b = 5
        a = "test/input/one_digit_section_id.csv"
        table, key_fields, header, duplicate_rows = table_ops.read_table(a, True)
        print(table)
        self.assertEqual(7, len(table))
        self.assertEqual(1, len(duplicate_rows))
        self.assertEqual('3', table[2][static_data.cdd_info_only_header.index(SECTION_ID)])

    def test_search_on_files(self, ):
        rd = RxData()
        search_info = dict()
        search_info[static_data.SEARCH_TERMS] = "for  while public".split(' ')
        rd.search_on_files(search_info)

    def test_search2(self, ):
        scheduler = TestScheduler()
        interval_time = 300
        rd = RxData()
        pipe = rd.do_search("test/input/four_line_created.csv", scheduler).pipe(
            ops.map(lambda count: my_print(count,
                                           "test test_table_dict[{}]\n")))

        # .subscribe(lambda key, row: self.assertTupleEqual())

        def create():
            return pipe

        subscribed = 300
        disposed = 1800
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
        print(results.messages)


def accum(acc: list, a):
    return list(acc).append(a)


def my_write(v: Any, f: Any = '{}'):
    print(f.format(v))
    return v


def bla(thing):
    print(thing)
    return thing


if __name__ == "__main__":
    unittest.main()
