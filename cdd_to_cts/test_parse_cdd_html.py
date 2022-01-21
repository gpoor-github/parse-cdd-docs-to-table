from unittest import TestCase

import parse_cdd_html


class Test(TestCase):
    def test_download_file(self):
        parse_cdd_html.download_file()
