import os
import unittest

import rx
from rx import operators as ops

from cdd_to_cts import static_data, helpers
from cdd_to_cts.react import RxData, my_print


def my_map_dict(key: str, m_list: list) -> list:
    # mysubject = ReplaySubject()
    dict_list = list()
    for item in m_list:
        if ord(item[0]) > ord('a'):
            key = item
        else:
            dict_list.append('[{}:{}]'.format(key, item))
    return dict_list


class MyTestCase(unittest.TestCase):

    def test_filtered_cdd_by_table(self, ):
        RxData().get_filtered_cdd_by_table(static_data.INPUT_TABLE_FILE_NAME, "input/cdd.html").pipe(
            ops.map(lambda v: my_print(v)),
            ops.count(),
            ops.map(lambda count: my_print(count, "count ={}"))). \
            subscribe(lambda count: self.assertEqual(count, 80))

        print("done")

    def test_rx_at_test_methods_to_words(self, ):
        RxData().get_at_test_method_words(static_data.TEST_FILES_TXT). \
            pipe(ops.map(lambda v: my_print(v)),
                 ops.count()). \
            subscribe(lambda count: self.assertEqual(count, 964))

    def test_search_terms(self, ):
        RxData().get_search_terms( static_data.CDD_REQUIREMENTS_FROM_HTML_FILE). \
            pipe(ops.map(lambda req: my_print(req, 'search in test[{}]\n'))).subscribe()

    # Callable[[TState, T1], TState]
    def reduce_find(self, term, target):
        print(f'{term} {target}')
        return target.split(":")[0]

    def predicate(self,  target)-> bool:
        print("hey "+ str(target))
        terms = str(target[0]).split(' ')

        thing_to_search = helpers.read_file_to_string(target[1].split(' :')[0])
        is_found=False
        for term in terms:
            term.strip(')')
            is_found = thing_to_search.find(term) > -1
            if is_found:
                break
        return is_found

    def does_match(self, target: str, search_terms: rx.Observable) -> rx.Observable:
        return search_terms.pipe(ops.reduce(lambda term: self.reduce_find(term, target)))
        # return search_terms.pipe(ops.find(lambda item: self.does_match_item(target,search_terms)))
    match = False
    def does_match_item(self, target: str, o_term:rx.Observable) -> bool:
        # val = term.lock
        val = True
        o_term.pipe(ops.map(lambda v: my_print(v,"a{}")),ops.to_list(),ops.map(lambda v: my_print(v,"b{}")),
                           ops.filter(lambda term: self.predicate(term)), ops.flat_map(rx.just(False)))
        return self.match
        # term = o_term.pipe(ops.first(),o

        # if target.find(term) > -1:
        #     print(f"does_match_item term {term}")
        #     return rx.just(target)
        # else:
        #     return rx.empty()

    def do_manual_search(self, target: str, search_terms: rx.Observable) -> rx.Observable:
        return search_terms.pipe(ops.do_while(lambda term: self.does_match_item(target, term)),
                                 ops.to_list())
        # return search_terms.pipe(ops.find(lambda item: self.does_match_item(target,search_terms)))

    def test_cdd_html_to_requirements(self, ):
        RxData().get_cdd_html_to_requirements("../input/cdd-11-mod-test.txt").pipe(
            ops.map(lambda v: my_print(v)),
            ops.count(),
            ops.map(lambda count: my_print(count, "count ={}"))). \
            subscribe(lambda count: self.assertEqual(count, 1370))

    def test_search(self, ):
        rd = RxData()
        rd.get_search_terms(static_data.CDD_REQUIREMENTS_FROM_HTML_FILE).pipe(
            ops.take(100),
            ops.combine_latest(rd.get_replay_of_at_test_files()),
           # ops.map(lambda req: my_print(req, 'search combine_latest[{}]')),
            ops.filter(lambda tuple1 : self.predicate(tuple1) ),
            ops.map(lambda req: my_print(req, 'Matched !!combine_latest[{}]')),
            ops.count()).subscribe(lambda count: self.assertEqual(count, 1370))

    def test_search2(self, ):
        rd = RxData()
        rd.get_at_test_method_words( static_data.TEST_FILES_TXT).pipe(
            ops.take(50),
            ops.flat_map(lambda method_words: self.does_match(method_words, RxData().get_search_terms(
                 static_data.CDD_REQUIREMENTS_FROM_HTML_FILE))),
            ops.count()).subscribe(lambda count: self.assertGreater(count, 2, f" Count {count}"))


if __name__ == '__main__':
    unittest.main()

    print(os.path.join(os.path.dirname(__file__),
                       '..',
                       'resources'
                       'datafile1.txt'))
