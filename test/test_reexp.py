import time
import unittest
from typing import Any

import rx
from rx import operators as ops
from rx.testing import TestScheduler

from cdd_to_cts import static_data, helpers, react, table_ops
from cdd_to_cts.react import RxData, my_print


def my_print2(v: Any, f: Any = '{}'):
    print(f.format(v))
    print(len(v[1]))
    return v


def predicate3(target, i, source) -> bool:
    print("predicate 3 " + str(target))

    return True


def predicate2(target, i, source) -> bool:
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

    def test_search_terms(self, ):
        rd = RxData()
        rd.get_search_terms(rd.get_cdd_html_to_requirements(static_data.CDD_REQUIREMENTS_FROM_HTML_FILE)) \
            .pipe(ops.map(lambda v: my_print(v)),
                  ops.count()). \
            subscribe(lambda count: self.assertEqual(count, 1317))

    # Callable[[TState, T1], TState]
    def reduce_find(self, term, target):
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
        rd.get_search_terms(rd.get_filtered_cdd_by_table("./input/test_manual_search.csv", "input/cdd.html")).pipe(
            ops.map(lambda req: react.get_search_terms(req))).subscribe(
            lambda terms: my_print(terms, "manual_search {}"))

    def test_search(self, ):
        rd = RxData()
        rd.get_search_terms(rd.get_filtered_cdd_by_table("input/new_recs_remaining_todo.csv", "input/cdd.html")).pipe(
            ops.map(lambda req: my_print(req, "find_search_terms[{}]")),
            ops.combine_latest(rd.get_replay_of_at_test_files_only()),

            ops.filter(lambda result: dict(result).get("search_result")),
            ops.map(lambda req: my_print(req, "find_search_result[{}]")),

            ops.map(lambda v: my_print2(v, "find_downstream_search_result[{}]")),
            ops.count()).subscribe(lambda count: self.assertEqual(count, 32))

    def test_do_search_unfiltered_on_results(self, ):
        rd = RxData()
        rd.do_search("input/new_recs_remaining_todo.csv", "input/cdd.html").pipe(
            ops.map(lambda req: my_print(req, "test_do_search[{}]")),
            ops.count()).subscribe(lambda count: self.assertEqual(count, 80))

    def test_do_search(self, ):
        rd = RxData()
        rd.do_search("./input/full_cdd.csv", "./input/cdd.html").pipe(
            ops.filter(lambda result: dict(result).get("search_result")),
            ops.map(lambda req: my_print(req, "test_do_search[{}]")),
            ops.count()).subscribe(lambda count: self.assertEqual(count, 21))

    def test_handle_search_results(self, ):
        rd = RxData()
        rd.do_search("input/full_cdd.csv", "input/cdd.html").pipe(
            ops.map(lambda result_dic: rd.find_data_for_csv_dict(result_dic)),
            ops.map(lambda v: my_print2(v, "test_handle_search_results[{}]")),

            ops.count(),
            ops.map(lambda count: my_print(count, "test_handle_search_results count[{}]")),
            ops.map(lambda count: self.assertEqual(count, 1316, " count for handle search results")),
        ).run()

    def test_handle_search_results_simplest(self, ):
        tdict = dict()
        rd = RxData()

        rx.just(tdict).pipe(
            ops.map(lambda result_dic: rd.find_data_for_csv_dict(result_dic)),
            ops.map(lambda v: my_print2(v, "find_data_for_csv_dict[{}]"))).subscribe()

    def test_handle_search_results_debug(self, ):
        scheduler = TestScheduler()
        rd = RxData()
        composed = rd.do_search("input/full_cdd.csv", "input/cdd.html", scheduler=scheduler)

        # composed.subscribe()

        def create():
            return composed

        subscribed = 300
        disposed = 1400
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
        print(results.messages)
        self.assertRegexpMatches(str(results.messages), "3.2.3.5/C-4-1")

        print("done")

    def test_handle_search_results_to_csv7(self, ):
        rd = RxData()
        rd.test_handle_search_results_to_csv("./input/full_cdd.csv", "./input/cdd.html"). \
            pipe(
            #ops.filter(lambda ag_results: len(ag_results[1])>1),
            ops.map(lambda v: my_print2(v, "test_handle_search_results_to_csv2[{}]"))).run()

    def test_handle_search_results_to_csv(self, ):
        rd = RxData()
        rd.test_handle_search_results_to_csv("./input/full_cdd.csv", "./input/cdd.html") \
            .subscribe(
            on_next=lambda table: table_ops.write_table("./output/rx_try3.csv", table, static_data.new_header))
        # .pipe(
        # ops.map(lambda result_dic: rd.find_data_for_csv_dict(result_dic)),
        #   ops.filter(lambda result: dict(result).get("search_result")),
        # ops.map(lambda result_dic: react.publish_results(result_dic, static_data.new_header)),
        #  ops.to_list(),
        # ops.map(lambda v: my_print2(v, "after tolist[{}]"))) \

        #  ops.reduce(lambda acc, a: accum2(acc, " ".join(a), seed=[]))).\
        #  subscribe(on_next=lambda result: my_write(result, "test_reducer  ={}"))

    def test_reducer(self, ):
        rx.from_iterable(range(10)).pipe(ops.reduce(lambda acc, a: acc + list(a), seed=[])
                                         ).subscribe(on_next=lambda result: my_write(result, "test_reducer  ={}"))

    def test_reducer2(self, ):
        rx.from_iterable(range(10)).pipe(ops.reduce(lambda acc, a: accum(acc, a), seed=[])
                                         ).subscribe(on_next=lambda result: my_write(result, "test_reducer  ={}"))


def accum(acc, a):
    return acc + [a]


def accum2(acc, a):
    return acc


def my_write(v: Any, f: Any = '{}'):
    print(f.format(v))
    return v


def bla(thing):
    print(thing)
    return thing


if __name__ == "__main__":
    unittest.main()
