#  Block to comment

from unittest import TestCase

import parser_helpers
import static_data
from parser_helpers import create_full_table_from_cdd


class Test(TestCase):
        def test_parse_cdd_12_html_full(self, ):
            full_cdd_html = parser_helpers.find_valid_path(
                "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/input/cdd_12_download.html")
            from parse_cdd_html import parse_cdd_html_to_requirements
            key_to_full_requirement_text_local, cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(
                full_cdd_html)
            create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                                       section_to_section_data,
                                       "./output/cdd_12_gen_html.tsv", static_data.cdd_info_only_header)
            self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
            self.assertIsNotNone(key_to_full_requirement_text_local.get("7.1.1.1/W-0-1"))
            self.assertIsNotNone(key_to_full_requirement_text_local.get("7.2.3/W-0-1"))
            self.assertEqual(1729, len(key_to_full_requirement_text_local))
