from typing import Any
from unittest import TestCase

import rx
from rx.testing import TestScheduler

import table_ops
from react import RxData
from rx import operators as ops, pipe

from static_data import HEADER_KEY


def my_print(v: Any, f: Any = '{}'):
    print(f.format(v))
    return v

class TestUpdate(TestCase):
    def test_get_input_table_keyed(self, ):
            scheduler = TestScheduler()
            header = ["Section", "section_id", "req_id", "full_key", "requirement", "manual_search_terms"]

            table_dict, header = table_ops.read_table_key_at_index("test/input/get_input_table_key_index_mod.csv,",
                                                                   header.index("full_key"))
            pipe = rx.from_iterable(table_dict, scheduler).pipe(ops.map(lambda key: (key, table_dict.get(key))),
                                                                ops.map(lambda tdict: my_print(tdict,
                                                                                               "test test_table_dict[{}]\n")))

            # .subscribe(lambda key, row: self.assertTupleEqual())

            def create():
                return pipe

            subscribed = 300
            disposed = 1800
            results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
            print(results.messages)
            # self.assertCountEqual("Section,section_id,req_id,requirement".split(','), dict(table_dict).get(HEADER_KEY))

            t0 = (0, ['Section', 'section_id', 'req_id', 'requirement'])
            r1 = ",3.2.3.5,C-4-1,req-c-4-1".split(',')
            r2 = ",3.2.3.5,C-5-1,req-c-5-1".split(',')
            r3 = ",3.2.3.5,C-5-2,req-c-5-2".split(',')
            r4 = ",3.2.3.5,C-6-1,req-c-6-1".split(',')
            k1 = "3.2.3.5/C-4-1"
            k2 = "3.2.3.5/C-5-1"
            k3 = "3.2.3.5/C-5-2"
            k4 = "3.2.3.5/C-6-1"

