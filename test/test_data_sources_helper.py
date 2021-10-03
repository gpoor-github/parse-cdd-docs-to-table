from unittest import TestCase

import helpers
import static_data


class TestParse(TestCase):
    def test_parse_cdd_html_to_requirements(self):
        full_cdd_html = helpers.find_valid_path("/input/cdd.html")

        from cdd_to_cts.data_sources_helper import parse_cdd_html_to_requirements
        key_to_full_requirement_text_local, key_to_java_objects_local, key_to_urls_local, \
            cdd_requirements_file_as_string, section_to_section_data = parse_cdd_html_to_requirements(full_cdd_html)

        value =key_to_full_requirement_text_local.get("3/C-0-1")

        self.assertIsNotNone(key_to_full_requirement_text_local.get("3.2.3.1/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-1"))
        self.assertIsNotNone(key_to_full_requirement_text_local.get("3/W-0-2"))
        self.assertRegex(key_to_full_requirement_text_local.get("3.1/C-0-1"),"MUST provide complete implementations, including all documented behaviors, of any documented API exposed by the Android SDK or any API decorated with the ".replace(',',';'))
        self.assertRegex(key_to_full_requirement_text_local.get("9.16/C-1-2"),"MUST securely confirm the primary authentication on the source device and confirm with the user intent to copy the data on the source device before any data is transferred.")
        self.assertEqual(1593, len(key_to_full_requirement_text_local))
