from unittest import TestCase


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
