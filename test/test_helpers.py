from unittest import TestCase

import helpers
import static_data


class Test(TestCase):
    def test_add_list_to_dict(self):
        adic: dict = dict()
        adic['1'] = 'a'
        adic['2'] = 'c'
        from cdd_to_cts.helpers import add_list_to_dict
        adic = add_list_to_dict("b", adic, '1')
        self.assertEqual('a b', adic.get('1'))

    def test_cleanhtml(self):
        self.fail()

    def test_find_full_key(self):
        self.fail()

    def test_remove_n_spaces_and_commas(self):
        self.fail()

    def test_bag_from_text(self):
        self.fail()


    def test_convert_version_to_number_from_full_key(self):
        self.fail()

    def test_convert_version_to_number(self):
        self.fail()

    def test_raise_error(self):
        self.fail()

    def test_process_requirement_text(self):
        self.fail()


    def test_add_to_count_dict_add_sets_helper(self):
        search_results = dict()
        a="a"
        b="b"
        c="c"
        s1 = {a, b}
        s2 = set({c,b})
        helpers.add_list_to_count_dict(s1,search_results,static_data.MATCHED_TERMS)
        cd = search_results.get(static_data.MATCHED_TERMS)
        self.assertEqual(1,cd.count_value_dict.get(a))
        self.assertEqual(1,cd.count_value_dict.get(b))

        helpers.add_list_to_count_dict(s1,search_results,static_data.MATCHED_TERMS)
        self.assertEqual(2,cd.count_value_dict.get(a))
        self.assertEqual(2,cd.count_value_dict.get(b))

        helpers.add_list_to_count_dict(s2,search_results,static_data.MATCHED_TERMS)
        self.assertEqual(2, cd.count_value_dict.get(a))
        self.assertEqual(3, cd.count_value_dict.get(b))

        str1 =     sorted(cd.count_value_dict.items(), key=lambda x: x[1], reverse=True)
        print (str1)

    def test_add_to_count_dict_add_sets(self):
        cd = helpers.CountDict()
        a="a"
        b="b"
        c="c"
        s1 = {a, b}
        s2 = set({c,b})
        count_dictionary = dict()
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
        cd2 = helpers.CountDict()
        a="a"
        b="b"
        count_dictionary = dict()
        cd2.add_to_count_dict(a)
        self.assertEqual(1,cd2.count_value_dict.get(a))
        cd2.add_to_count_dict(a)
        self.assertEqual(2,cd2.count_value_dict.get(a))
        cd2 = None

    def test_find_urls(self):
        self.fail()

    def test_find_java_objects(self):
        self.fail()

    def test_find_section_id(self):
        self.fail()

    def test_make_files_to_string(self):
        self.fail()

    def test_read_file_to_string(self):
        self.fail()

    def test_build_composite_key(self):
        self.fail()


    def test_build_test_cases_module_dictionary(self):
        self.fail()
