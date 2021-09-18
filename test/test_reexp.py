import os
import unittest

import rx
from rx import operators as ops

from cdd_to_cts import static_data
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
        RxData().get_filtered_cdd_by_table("../" + static_data.INPUT_TABLE_FILE_NAME, "input/cdd.html").pipe(
            ops.map(lambda v: my_print(v)),
            ops.count(),
            ops.map(lambda count: my_print(count, "count ={}"))). \
            subscribe(lambda count: self.assertEqual(count, 80))

        print("done")

    def test_rx_at_test_methods_to_words(self, ):
        RxData().get_at_test_method_words("../" + static_data.TEST_FILES_TXT). \
            pipe(ops.map(lambda v: my_print(v)),
                 ops.count()). \
            subscribe(lambda count: self.assertEqual(count, 964))

    def test_search_terms(self, ):
        RxData().get_search_terms("../" + static_data.CDD_REQUIREMENTS_FROM_HTML_FILE). \
            pipe(ops.map(lambda req: my_print(req, 'search in test[{}]\n'))).subscribe()

    def does_match(self, target: str, search_terms: rx.Observable) -> rx.Observable:
        return search_terms.pipe(ops.find(lambda item: self.does_match_item(target,search_terms)))

    def does_match_item(self, target: str, term: rx.Observable) -> bool:
        print(f"does_match_item term {term}")
        return target.find(target) > -1

    def test_cdd_html_to_requirements(self, ):
        RxData().get_cdd_html_to_requirements("../input/cdd-11-mod-test.txt").pipe(
            ops.map(lambda v: my_print(v)),
            ops.count(),
            ops.map(lambda count: my_print(count, "count ={}"))). \
            subscribe(lambda count: self.assertEqual(count, 1370))

    def test_search(self, ):
        RxData().get_at_test_method_words("../" + static_data.TEST_FILES_TXT).pipe(
                 ops.flat_map(lambda method_words: self.does_match(method_words,
                                                                   RxData().get_search_terms(
                                                                       "../" + static_data.CDD_REQUIREMENTS_FROM_HTML_FILE))),
                 ops.map(lambda req: my_print(req, 'search result[{}]\n')),
                 ops.count()). \
            subscribe(lambda count: self.assertLess(count, 2, f" Count {count}"))


    def test_search2(self, ):
        RxData().get_at_test_method_words("../" + static_data.TEST_FILES_TXT).pipe(
            ops.take(50),
            ops.flat_map(lambda method_words: self.does_match(method_words, RxData().get_search_terms(
                "../" + static_data.CDD_REQUIREMENTS_FROM_HTML_FILE))),
                    ops.count()).subscribe(lambda count: self.assertGreater(count, 2,f" Count {count}"))

if __name__ == '__main__':
    unittest.main()

    print(os.path.join(os.path.dirname(__file__),
                       '..',
                       'resources'
                       'datafile1.txt'))
