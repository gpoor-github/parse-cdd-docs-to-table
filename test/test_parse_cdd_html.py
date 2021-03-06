#  Block to comment

from unittest import TestCase

from cdd_to_cts import parser_helpers, parser_constants
from cdd_to_cts.parse_cdd_html import parse_cdd_html_to_requirements
from cdd_to_cts.parser_helpers import create_full_table_from_cdd


class Test(TestCase):
        def test_parse_cdd_12_html_full(self, ):
            full_cdd_html = parser_helpers.find_valid_path(
                "./input/cdd_12_download.html")
            key_to_full_requirement_text_local, cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(
                full_cdd_html)
            self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
            self.assertIsNotNone(key_to_full_requirement_text_local.get("7.1.1.1/W-0-1"))
            self.assertIsNotNone(key_to_full_requirement_text_local.get("7.2.3/W-0-1"))
            self.assertEqual(1729, len(key_to_full_requirement_text_local))


        def test_parse_cdd_12_html_full_and_create_file(self, ):
            full_cdd_html = parser_helpers.find_valid_path(
                "./input/cdd_12_download.html")
            key_to_full_requirement_text_local, cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(
                full_cdd_html)
            create_full_table_from_cdd(key_to_full_requirement_text_local, key_to_full_requirement_text_local,
                                       section_to_section_data,
                                       "./output/cdd_12_gen_html.tsv", parser_constants.cdd_info_only_header)
