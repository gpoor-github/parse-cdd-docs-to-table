from unittest import TestCase

from cdd_to_cts import parse_cdd_html


class Test(TestCase):
    def test_download_file(self):
        parse_cdd_html.download_file()
        self.fail()
