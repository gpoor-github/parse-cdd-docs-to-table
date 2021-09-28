from unittest import TestCase

from react import RxData
from static_data import DEFAULT_SECTION_ID_INDEX


class TestAddToDict(TestCase):
    def test_add_to_dic(self):
        a_7_line_table = "test/input/section_id_length_one_issue.html"
        rd = RxData()
        rd.cdd_html_to_requirements_csv(a_7_line_table). \
            subscribe(lambda table_dict: self.assertEqual('3', table_dict[2][DEFAULT_SECTION_ID_INDEX]))