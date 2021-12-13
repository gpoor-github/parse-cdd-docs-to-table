#  Block to comment
import os
import unittest

import rx
from rx import operators as ops
from rx.testing import TestScheduler, ReactiveTest

import data_sources
from cdd_to_cts import static_data, parser_helpers
from cdd_to_cts.react import RxData, my_print
from parser_helpers import create_full_table_from_cdd
from parse_cdd_md import parse_cdd_md


class ParseHTMLTests(unittest.TestCase):
    def test_get_input_table_keyed(self, ):
        scheduler = TestScheduler()
        header = ["Section", "section_id", "req_id", "full_key", "requirement", "manual_search_terms"]
        rd = RxData()

        table_dict, header = rd.init_input_table_keyed("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/four_line_sparse.tsv")
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
            ReactiveTest.on_next(300, (k1, r1)),
            ReactiveTest.on_next(300, (k2, r2)),
            ReactiveTest.on_next(300, (k3, r3)),
            ReactiveTest.on_next(300, (k4, r4)),
            ReactiveTest.on_completed(300)
        ]

    def test_parse_cdd_12_html_full(self, ):
        full_cdd_html = parser_helpers.find_valid_path(
            "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_download.html")
        from parse_cdd_html import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local,  cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(full_cdd_html)
        create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                                   section_to_section_data,
                                   "./output/cdd_12_gen_html.tsv", static_data.cdd_info_only_header)
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.1.1.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.2.3/W-0-1"))
        self.assertEqual(1729, len(key_to_full_requirement_text_local))

    def test_parse_cdd_12_html_missed_7_11(self, ):
        full_cdd_html = parser_helpers.find_valid_path(
            "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/html_parsing_7-11_issue.html")
        from parse_cdd_html import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local,  \
        cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(full_cdd_html)
        create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                                   section_to_section_data,
                                   "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/output/html_parsing_7-11_issue.tsv", static_data.cdd_info_only_header)
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.11/C-1-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.11/C-1-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("8"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("8.1"))

        self.assertEqual(8, len(key_to_full_requirement_text_local))

    def test_parse_cdd_11_html_full(self, ):
        full_cdd_html = parser_helpers.find_valid_path(
            "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_download.html")
        from parse_cdd_html import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local,  \
        cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(full_cdd_html)
        create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                                   section_to_section_data,
                                   "./output/cdd_11_gen_html.tsv", static_data.cdd_info_only_header)

        self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.1.1.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.2.3/W-0-1"))
        self.assertEqual(1556, len(key_to_full_requirement_text_local))

    def test_parse_cdd_html_to_short_file_only_7(self, ):
        a_7_line_table = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/just_one_section_id_digit_issue.html"
        cwd = os.getcwd()
        static_data.WORKING_ROOT = cwd + "/"
        scr = data_sources.SourceCrawlerReducer(a_7_line_table)

        key_to_full_requirement_text_local = scr.key_to_full_requirement_text
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-2"))
        self.assertEqual(4, len(key_to_full_requirement_text_local))

    def test_parse_cdd_html_to_requirements_problem(self):
        problem_file= "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/problem_subset_cdd_12_wrong_section.html"

        from parse_cdd_html import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local,  \
        cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(problem_file)
        create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                                   section_to_section_data,
                                   "./output/html_cdd_12_master.tsv", static_data.cdd_info_only_header)

        value = key_to_full_requirement_text_local.get("5.1/H-1-1")

        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.5/H-1-2"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("5.1/H-1-8"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("6.1/H-0-6"))
        self.assertTrue(key_to_full_requirement_text_local.get("3.1/C-0-1").find(
                         "MUST provide complete implementations, including all documented behaviors, of any documented API exposed by the Android SDK or any API decorated with the ") > -1)
        self.assertTrue(key_to_full_requirement_text_local.get("3.2.2/C-0-1").find("C-0-1] To provide consistent, meaningful values across device") > -1)
        self.assertEqual(59, len(key_to_full_requirement_text_local))

    def test_parse_cdd_html_to_requirements(self):
        full_cdd_html = parser_helpers.find_valid_path("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/android-12-cdd_2021_11_22.html")
        from parse_cdd_html import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local,  \
        cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(full_cdd_html)
        create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                                   section_to_section_data,
                                   "./output/html_cdd_12_downloaded_2021_11_22.tsv", static_data.cdd_info_only_header)


        self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.1.1.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.2.3/W-0-1"))
        self.assertTrue(key_to_full_requirement_text_local.get("3.2.2/C-0-1").find("C-0-1] To provide consistent, meaningful values across device") > -1)
        self.assertEqual(1593, len(key_to_full_requirement_text_local))

    def test_parse_cdd_11_html_to_requirements(self):
        full_cdd_html = parser_helpers.find_valid_path("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_11_download.html")
        from parse_cdd_html import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local,  \
        cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(full_cdd_html)
        create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                                   section_to_section_data,
                                   "./output/cdd_11_gen_html.tsv", static_data.cdd_info_only_header)


        self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.1.1.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.2.3/W-0-1"))
        self.assertTrue(key_to_full_requirement_text_local.get("3.2.2/C-0-1").find("C-0-1] To provide consistent, meaningful values across device") > -1)
        self.assertEqual(1593, len(key_to_full_requirement_text_local))

    def test_parse_cdd_section_issue(self):
        full_cdd_html = parser_helpers.find_valid_path("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/section_issue.html")
        from parse_cdd_html import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local,  \
        cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(full_cdd_html)
        create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                                   section_to_section_data,
                                   "./output/section_issue.tsv", static_data.cdd_info_only_header)


        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.1.4.1/C-0-1"))

    def test_parse_cdd_html_to_short_file_only_7_md(self, ):

        key_to_full_requirement_text_local, section_to_section_data = parse_cdd_md("/home/gpoor/aosp_cdd/cdd")

        self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-2"))
        self.assertEqual(4, len(key_to_full_requirement_text_local))

    def test_parse_cdd_html_to_requirements_problem_md(self):
        key_to_full_requirement_text_local, section_to_section_data = parse_cdd_md("/home/gpoor/aosp_cdd/cdd")
        create_full_table_from_cdd( key_to_full_requirement_text_local, key_to_full_requirement_text_local,section_to_section_data,
                                "./output/md_cdd_12_master.tsv",static_data.cdd_info_only_header)
        value = key_to_full_requirement_text_local.get("5.1/H-1-1")
        self.assertIsNotNone(key_to_full_requirement_text_local.get("8.4/H-0-1"))

        # self.assertIsNotNone(key_to_full_requirement_text_local.get("7.5/H-1-1"))
        # self.assertIsNotNone(key_to_full_requirement_text_local.get("5.1/H-1-8"))
        # self.assertIsNotNone(key_to_full_requirement_text_local.get("6.1/H-0-6"))
        # self.assertTrue(key_to_full_requirement_text_local.get("3.1/C-0-1").find(
        #                  "MUST provide complete implementations, including all documented behaviors, of any documented API exposed by the Android SDK or any API decorated with the ") > -1)
        # self.assertTrue(key_to_full_requirement_text_local.get("3.2.2/C-0-1").find("C-0-1] To provide consistent, meaningful values across device") > -1)
        self.assertEqual(1382, len(key_to_full_requirement_text_local))

    def test_parse_md_9_problem(self):
        key_to_full_requirement_text_local, section_to_section_data = parse_cdd_md("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/cdd_9_problem"
                                                                                   ,logging=True)
        self.assertIsNotNone(key_to_full_requirement_text_local.get("9.8.1/C-0-1"))

        self.assertIsNotNone(key_to_full_requirement_text_local.get("9.6/C-1-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("9.7/C-0-1"))
        self.assertEqual(62, len(key_to_full_requirement_text_local))

    def test_parse_cdd_html_to_requirements_md(self):
        key_to_full_requirement_text_local, section_to_section_data = parse_cdd_md("/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/cdd_md_full_key")
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.1.1.1/H-1-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("7.2.4/H-0-1"))
        self.assertEqual(67, len(key_to_full_requirement_text_local))



if __name__ == '__main__':
    unittest.main()
