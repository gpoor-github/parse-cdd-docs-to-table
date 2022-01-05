from unittest import TestCase

import general_helpers
import parser_constants
import parser_helpers
import static_data


class TestHelpers1(TestCase):

    def test_clean_html(self):
        test_file = "/home/gpoor/PycharmProjects/parse-cdd-html-to-source/test/input/small_html_sample_with_http_anchor.html"
        html_str = parser_helpers.read_file_to_string(test_file)
        self.assertTrue(html_str.find("</a>") != -1)
        self.assertTrue(html_str.find("<title>" ) != -1)
        self.assertTrue(html_str.find("<!DOCTYPE html>" ) != -1)
        self.assertTrue(html_str.find("<a href=") != -1)
        self.assertTrue(html_str.find("7_1_display_and_graphics" ) != -1)
        html_str =  parser_helpers.cleanhtml(html_str)
        self.assertFalse(html_str.find("</a>" ) != -1)
        self.assertFalse(html_str.find("<title>" ) != -1)
        self.assertFalse(html_str.find("<!DOCTYPE html>" ) != -1)
        self.assertFalse(html_str.find("<a href=""#7_1_display_and_graphics"">7.1</a>.1.1/H-0-1] MUST have at least" ) != -1)
        self.assertFalse(html_str.find("7_1_display_and_graphics" ) != -1)
        self.assertTrue(html_str.find(" MUST have at least" ) != -1)
        self.assertFalse(html_str.find("href" ) != -1)



    def test_add_list_to_dict(self):
        a_dict: dict = dict()
        a_dict['1'] = 'a'
        a_dict['2'] = 'c'
        header = ['1']
        from general_helpers import add_list_to_dict
        a_dict = add_list_to_dict("b", a_dict, '1', header= header)
        self.assertEqual('a b', a_dict.get('1'))

    def test_add_to_count_dict_add_sets_helper(self):
        search_results = dict()
        a="a"
        b="b"
        c="c"
        s1 = {a, b}
        s2 = {c, b}
        general_helpers.add_list_to_count_dict(s1, search_results, parser_constants.MATCHED_TERMS)
        cd = search_results.get(parser_constants.MATCHED_TERMS)
        self.assertEqual(1,cd.count_value_dict.get(a))
        self.assertEqual(1,cd.count_value_dict.get(b))

        general_helpers.add_list_to_count_dict(s1, search_results, parser_constants.MATCHED_TERMS)
        self.assertEqual(2,cd.count_value_dict.get(a))
        self.assertEqual(2,cd.count_value_dict.get(b))

        general_helpers.add_list_to_count_dict(s2, search_results, parser_constants.MATCHED_TERMS)
        self.assertEqual(2, cd.count_value_dict.get(a))
        self.assertEqual(3, cd.count_value_dict.get(b))

        str1 =     sorted(cd.count_value_dict.items(), key=lambda x: x[1], reverse=True)
        print (str1)

    def test_add_to_count_dict_add_sets(self):
        cd = general_helpers.CountDict()
        a="a"
        b="b"
        c="c"
        s1 = {a, b}
        s2 = {c, b}
        cd.add_to_count_dict(s1)
        self.assertEqual(1,cd.count_value_dict.get(a))
        self.assertEqual(1,cd.count_value_dict.get(b))

        cd.add_to_count_dict(s1)
        self.assertEqual(2,cd.count_value_dict.get(a))
        self.assertEqual(2,cd.count_value_dict.get(b))

        cd.add_to_count_dict(s2)
        self.assertEqual(2, cd.count_value_dict.get(a))
        self.assertEqual(3, cd.count_value_dict.get(b))

    def test_add_to_count_dict_add_2(self):
        cd2 = general_helpers.CountDict()
        a="a"
        cd2.add_to_count_dict(a)
        self.assertEqual(1,cd2.count_value_dict.get(a))
        cd2.add_to_count_dict(a)
        self.assertEqual(2,cd2.count_value_dict.get(a))


