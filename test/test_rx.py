import time
import unittest

import rx
from rx.subject import Subject
from rx.testing import TestScheduler, ReactiveTest
from rx import Observable
from rx import operators as ops




class TestRx(unittest.TestCase):
    table = [[2, 4], [4, 5, 5],[4,9,8]]

    def test_interval(self):
        scheduler = TestScheduler()
        interval_time = 300

        def create():
            return rx.interval(interval_time, scheduler)

        subscribed = 300
        disposed = 1400
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
        print(results.messages)
        assert results.messages == [
            ReactiveTest.on_next(600, 0),
            ReactiveTest.on_next(900, 1),
            ReactiveTest.on_next(1200, 2),
        ]

    def test_list(self):
        scheduler = TestScheduler()
        interval_time = 300
        def create():
            return rx.from_list(self.table,scheduler=scheduler).pipe(ops.to_list())

        subscribed = 300
        disposed = 14000
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
        print(results.messages)

    def accum(self, acc, a):
        acc = acc + [a]
        print(acc)
        return acc

    def test_reduce(self):
        scheduler = TestScheduler()
        interval_time = 300

        def create():
            return rx.from_list(self.table,scheduler=scheduler).pipe(ops.reduce(lambda aac, a: self.accum(aac, a), seed=[]))

        subscribed = 300
        disposed = 12222
        results = scheduler.start(create, created=1, subscribed=subscribed, disposed=disposed)
        print(results.messages)
        assert results.messages == [
            ReactiveTest.on_next(600, 0)
        ]

    def test_custom_subject(self):
        scheduler = TestScheduler()
        self.mouse_click_stream = None
        self.click_count = 0

        def create(scheduler, state):
            self.mouse_click_stream = Subject()

        def click(scheduler, state):
            self.mouse_click_stream.on_next('clicked')

        def subscribe(scheduler, state):
            def update(i):
                self.click_count += 1

            self.mouse_click_stream.subscribe(update)

        scheduler.schedule_absolute(1, create)
        scheduler.schedule_absolute(2, click)
        scheduler.schedule_absolute(3, subscribe)
        scheduler.schedule_absolute(4, click)
        scheduler.schedule_absolute(5, click)
        results = scheduler.start()
        print(results.messages)
        assert self.click_count == 2


if __name__ == '__main__':
    unittest.main()
