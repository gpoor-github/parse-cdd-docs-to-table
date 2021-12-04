import time
import unittest
from typing import Any

import rx
from rx import operators as ops, pipe
from rx.testing import TestScheduler, ReactiveTest

from cdd_to_cts import static_data, helpers, react, table_ops
from cdd_to_cts.react import RxData, build_row, SEARCH_RESULT, build_dict, \
    created_and_populated_search_info_from_key_row_tuple, find_search_terms
from cdd_to_cts.static_data import SEARCH_TERMS, FULL_KEY, HEADER_KEY, SECTION_ID, DEFAULT_SECTION_ID_INDEX, \
    REQUIREMENT, MANUAL_SEARCH_TERMS


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
    is_match = False
    is_match = rx.Observable(source).pipe(ops.find(predicate=predicate3)).run()

    return is_match


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


class TestReacItems(unittest.TestCase):

    # def test_rx_at_test_methods_to_words(self, ):
    #     RxData().get_at_test_method_words(static_data.TEST_FILES_TXT). \
    #         pipe(ops.count()). \
    #         subscribe(lambda count: self.assertEqual(count, 1270))
    #

    # Callable[[TState, T1], TState]
    @staticmethod
    def reduce_find(term, target):
        print(f"{term} {target}")
        return target.split(":")[0]

    def does_match(self, target: str, search_terms: rx.Observable) -> rx.Observable:
        return search_terms.pipe(ops.reduce(lambda term: self.reduce_find(term, target)))
        # return search_terms.pipe(ops.find(lambda item: self.does_match_item(target,search_terms)))

    match = False

    # def predicate(self, target) -> bool:
    #     # print("predicate " + str(target))
    #     result = self.execute_search_on_file_for_terms_return_results(target)
    #     if result.get(SEARCH_RESULT):
    #         self.result_subject.on_next(result)
    #         return True
    #     return False
    # def does_match_item(self, target: str, o_term: rx.Observable) -> bool:
    #     # val = term.lock
    #     val = True
    #     o_term.pipe(ops.map(lambda v: my_print(v, "a{}")), ops.to_list(), ops.map(lambda v: my_print(v, "b{}")),
    #                 ops.filter(lambda term: RxData().predicate(term)), ops.flat_map(rx.just(False)))
    #     return self.match
    #     # term = o_term.pipe(ops.first(),o
    #
    #     # if target.find(term) > -1:
    #     #     print(f"does_match_item term {term}")
    #     #     return rx.just(target)
    #     # else:
    #     #     return rx.empty()
    #
    # # def test_rx_find(self, ):
    # #     rd = RxData()
    # #     rd.get_replay_of_at_test_files().pipe(ops.find(predicate2)).subscribe()
    # def get_replay_read_table(self, file_name: str = static_data.INPUT_TABLE_FILE_NAME_RX) -> [ReplaySubject,
    #                                                                                            ReplaySubject]:
    #
    #     if self.__replay_input_table and self.__replay_header:
    #         return self.__replay_input_table, self.__replay_header
    #     else:
    #         self.__replay_input_table = ReplaySubject(1500)
    #         self.__replay_header = ReplaySubject(50)
    #
    #     section_id_index = 1
    #     req_id_index = 2
    #     duplicate_rows: [str, str] = dict()
    #     if file_name.find(static_data.WORKING_ROOT) == -1:
    #         file_name = static_data.WORKING_ROOT + file_name
    #     try:
    #         with open(file_name) as csv_file:
    #
    #             csv_reader_instance: [str] = csv.reader(csv_file, delimiter=',')
    #             table_index = 0
    #
    #             for row in csv_reader_instance:
    #                 if table_index == 0:
    #                     try:
    #                         section_id_index = row.index(SECTION_ID)
    #                         req_id_index = row.index(REQ_ID)
    #                         print(f'Found header for {file_name} names are {", ".join(row)}')
    #                         self.__replay_header.on_next(row)
    #                         self.__replay_header.on_completed()
    #                         table_index += 1
    #
    #                         # Skip the rest of the loop... if there is an exception carry on and get the first row
    #                         continue
    #                     except ValueError:
    #                         message = f' Error: First row NOT header {row} default to section_id = col 1 and req_id col 2. First row of file {csv_file} should contain CSV with header like Section, section_id, etc looking for <Section> not found in {row}'
    #                         print(message)
    #                         raise SystemExit(message)
    #                         # Carry on and get the first row
    #
    #                 # Section,section_id,req_id
    #                 section_id_value = row[section_id_index].rstrip('.')
    #                 req_id_value = row[req_id_index]
    #                 if len(req_id_value) > 0:
    #                     key_value = '{}/{}'.format(section_id_value, req_id_value)
    #                 elif len(section_id_value) > 0:
    #                     key_value = section_id_value
    #
    #                 self.__replay_input_table.on_next(f'{key_value}:{row}')
    #
    #             if len(duplicate_rows) > 0:
    #                 print(
    #                     f"ERROR, reading tables with duplicate 1 {file_name} has={len(duplicate_rows)} duplicates {duplicate_rows} ")
    #
    #         self.__replay_input_table.on_completed()
    #
    #         return self.__replay_input_table, self.__replay_header
    #     except IOError as e:
    #         helpers.print_system_error_and_dump(f"Failed to open file {file_name} exception -= {type(e)} exiting...")
    #
    # def get_filtered_cdd_by_table(self, input_table_file=static_data.INPUT_TABLE_FILE_NAME_RX,
    #                               cdd_requirements_file=static_data.CDD_REQUIREMENTS_FROM_HTML_FILE,
    #                               scheduler: rx.typing.Scheduler = None) -> rx.Observable:
    #
    #     table_dic = observable_to_dict(self.get_replay_read_table(input_table_file)[0])
    #     return self.get_cdd_html_to_requirements(cdd_requirements_file, scheduler) \
    #         .pipe(ops.filter(lambda v: table_dic.get(str(v).split(':', 1)[0])))

    # def init_input_table(self, table_dict_file=static_data.INPUT_TABLE_FILE_NAME_RX):
    #     # input_table, input_table_keys_to_index, input_header, duplicate_rows =
    #     if not self.__input_header:
    #         import table_ops
    #         self.__input_table, self.__input_table_keys, self.__input_header, duplicate_row = table_ops.read_table_sect_and_req_key(
    #             table_dict_file)
    #     return self.__input_table, self.__input_table_keys, self.__input_header

    def test_replay_simple_at_test_file_only(self, ):
        start = time.perf_counter()
        rd = RxData()
        for i in range(0, 2):
            rd.get_replay_of_at_test_files_only().pipe(ops.count()).subscribe(
                on_next=lambda result: my_print(result, "test_replay_simple_at_test_file_only  ={}"))
        end = time.perf_counter()
        print(f"Took time {end - start:0.4f}sec ")

    def test_create_initial_search_info(self, ):
        header = ['Section', 'section_id', 'req_id', 'full_key', 'requirement', 'yes_2', 'manual_search_terms']
        row = ['s', '5.1', 'H-1-1', '5.1/H-1-1', '5.1/H-1-1: juicyTestFunction()', 'yes_2','secure screen lock verification']
        expected = {'secure', 'screen', 'lock', 'verification'}
        search_info = created_and_populated_search_info_from_key_row_tuple(('5.1/H-1-1',row), header)


        self.assertEqual('5.1/H-1-1: juicyTestFunction()', search_info.get(static_data.REQUIREMENT))
        self.assertEqual('secure screen lock verification', search_info.get(static_data.MANUAL_SEARCH_TERMS))
        self.assertEqual('5.1/H-1-1', search_info.get(static_data.FULL_KEY))
        return search_info

    def test_manual_search_terms(self, ):
        search_info=  self.test_create_initial_search_info()
        find_search_info = find_search_terms(search_info)
        self.assertEqual('secure screen lock verification', search_info.get(static_data.MANUAL_SEARCH_TERMS))
        self.assertEqual('5.1/H-1-1', search_info.get(static_data.FULL_KEY))
        self.assertIsNot(None,find_search_info.get(static_data.SEARCH_TERMS))
        self.assertIsNot(None,search_info.get(static_data.SEARCH_TERMS))
        self.assertIsNot(None,search_info.get(static_data.AUTO_SEARCH_TERMS))
        expected_manual = {'secure', 'screen', 'lock', 'verification'}
        expected_auto = {'5.1', 'H-1-1', 'juicyTestFunction()', '5.1/H-1-1'}

        self.assertSetEqual(expected_auto, find_search_info.get(static_data.AUTO_SEARCH_TERMS))
        self.assertIs('secure screen lock verification', find_search_info.get(static_data.MANUAL_SEARCH_TERMS))
        self.assertSetEqual(expected_manual.union(expected_auto), find_search_info.get(static_data.SEARCH_TERMS))

    def test_one_manual_search_terms(self, ):
        header = ['Section', 'section_id', 'req_id', 'full_key', 'requirement', 'yes_2', 'manual_search_terms']
        row = ['s', '5.1', 'H-1-1', '5.1/H-1-1', '5.1/H-1-1: juicyTestFunction()', 'yes_2',
               'foobarone']
        search_info = created_and_populated_search_info_from_key_row_tuple(('5.1/H-1-1', row), header)
        find_search_info = find_search_terms(search_info)
        self.assertEqual('foobarone', search_info.get(static_data.MANUAL_SEARCH_TERMS))
        self.assertEqual('5.1/H-1-1', search_info.get(static_data.FULL_KEY))
        self.assertIsNot(None,find_search_info.get(static_data.SEARCH_TERMS))
        self.assertIsNot(None,search_info.get(static_data.SEARCH_TERMS))
        self.assertIsNot(None,search_info.get(static_data.AUTO_SEARCH_TERMS))
        expected_manual = {'foobarone'}
        expected_auto = {'5.1', 'H-1-1', 'juicyTestFunction()', '5.1/H-1-1'}

        self.assertSetEqual(expected_auto, find_search_info.get(static_data.AUTO_SEARCH_TERMS))
        self.assertIs('foobarone', find_search_info.get(static_data.MANUAL_SEARCH_TERMS))
        self.assertSetEqual(expected_manual.union(expected_auto), find_search_info.get(static_data.SEARCH_TERMS))


    def test_manual_search_terms_bad_key(self, ):
        header = ['Section', 'section_id', 'req_id', 'full_key', 'requirement', 'yes_2', 'manual_search_terms']
        row = ['s', '5.1', 'H-1-1', '5.1/H-1-1', '5.1/H-1-1: req leave or copy', 'secure', 'screen', 'lock', 'verification']
        expected = {'secure', 'screen', 'lock', 'verification'}
        search_info = created_and_populated_search_info_from_key_row_tuple(row, header)
        self.assertEqual(None, search_info.get(static_data.MANUAL_SEARCH_TERMS))

    def test_handle_search_results_to_csv(self, ):
        scheduler = TestScheduler()
        rd = RxData()

        # .pipe(ops.map(lambda result_dic: react.publish_results(result_dic, static_data.cdd_to_cts_app_header)), ops.to_list(),
        #  ops.reduce(lambda acc, a: accum2(acc, " ".join(a), seed=[])))
        table, header = rd.init_input_table_keyed("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/four_line_created.csv")
        composed = rd.do_search(table, header, scheduler=scheduler).pipe(
            ops.map(lambda req: my_print(req, "test_handle_search_results_to_csv[{}]")),

            ops.filter(lambda search_info: dict(search_info).get(SEARCH_RESULT)),
            ops.map(lambda search_info: created_and_populated_search_info_from_key_row_tuple(search_info,
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


    def test_read_table_section_id_one_digit(self, ):
        b = 5
        a = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/one_digit_section_id.csv"
        table, key_fields, header, duplicate_rows = table_ops.read_table_sect_and_req_key(a, True)
        print(table)
        self.assertEqual(6, len(table))
        self.assertEqual(1, len(duplicate_rows))
        self.assertEqual('3', table[1][static_data.cdd_info_only_header.index(SECTION_ID)])

    def test_search_on_files(self, ):
        rd = RxData()
        rd.init_input_table_keyed("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/four_line_created.csv")
        search_info = dict()
        search_info[static_data.SEARCH_TERMS] = "for  while public".split(' ')
        rd.search_on_files(search_info)

    def test_search2(self, ):
        scheduler = TestScheduler()
        interval_time = 300
        rd = RxData()
        table, header = rd.init_input_table_keyed("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/four_line_created.csv")

        pipe = rd.do_search(table, header, scheduler).pipe(
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
