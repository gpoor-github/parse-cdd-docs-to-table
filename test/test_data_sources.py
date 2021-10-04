import os
from unittest import TestCase

import data_sources
import static_data


class TestSourceCrawlerReducer(TestCase):

    def test_parse_cdd_html_full(self, ):

        os.chdir('../')
        cwd = os.getcwd()
        static_data.WORKING_ROOT = cwd+"/"
        scr = data_sources.SourceCrawlerReducer()

        from cdd_to_cts.data_sources_helper import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local = scr.key_to_full_requirement_text
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-2"))
        self.assertEqual(1593, len(key_to_full_requirement_text_local))

    def test_parse_cdd_html_to_short_file_only_7(self, ):

        a_7_line_table = "test/input/just_one_section_id_digit_issue.html"
        cwd = os.getcwd()
        static_data.WORKING_ROOT = cwd + "/"
        scr = data_sources.SourceCrawlerReducer(a_7_line_table)


        from cdd_to_cts.data_sources_helper import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local = scr.key_to_full_requirement_text
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-2"))
        self.assertEqual(4, len(key_to_full_requirement_text_local))