import time
import queue
import unittest
from unittest import TestCase

from hdmi2usbmon.events import Event, EventDispatcher, EventHandler, EventTypeHandler


class BasicEvent(Event):
    def __init__(self, event_type='basic', data=None):
        super(BasicEvent, self).__init__(event_type=event_type, data=data)


class ErrorEvent(Event):
    def __init__(self, event_type='error', data=None):
        super(ErrorEvent, self).__init__(event_type=event_type, data=data)


class TestEvent(unittest.TestCase):

    # Utility classes

    def create_test_events(self):
        return (
            BasicEvent(),
            Event('general'),
            ErrorEvent(data={'error': 101, 'message': 'An error message'})
        )

    def common_test_event(self, *events):
        for event in events:
            # print('type(event.timestamp)={}'.format(type(event.timestamp)))
            self.assertLessEqual(event.timestamp, time.time())
            self.assertGreater(event.timestamp, time.time() - 100.0)
            self.assertIsInstance(event.event_type, (list, tuple))

    # Unit tests

    def test_event_types(self):
        self.common_test_event(*(self.create_test_events()))


class TestEventDispatcher(TestCase):

    def setUp(self):
        self.stats = dict()

    # Utility classes

    def create_dispatcher(self):
        dispatcher = EventDispatcher()
        return dispatcher

    def create_dispatcher_with_handlers(self):
        dispatcher = self.create_dispatcher()
        handler_list = (
            EventTypeHandler('basic', func=self.handler_basic),
            EventTypeHandler('general', func=self.handler_general),
            EventTypeHandler('error', func=self.handler_error)
        )
        for handler in handler_list:
            dispatcher.add_handler(handler)
        return dispatcher

    # Handlers

    def handler_basic(self, event):
        if 'basic' not in self.stats:
            self.stats['basic'] = 0
        self.stats['basic'] += 1
        print('Basic event callback #{}'.format(self.stats['basic']))

    def handler_general(self, event):
        if 'general' not in self.stats:
            self.stats['general'] = 0
        self.stats['general'] += 1
        print('General event callback #{}'.format(self.stats['basic']))

    def handler_error(self, event):
        if 'error' not in self.stats:
            self.stats['error'] = 0
        self.stats['error'] += 1
        print('Error event callback #{}'.format(self.stats['error']))

    # Unittests

    def test_dispatch_create(self):
        dispatcher = self.create_dispatcher()
        self.assertIsInstance(dispatcher, EventDispatcher)
        self.assertIsInstance(dispatcher.eventq, queue.Queue)
        self.assertIsInstance(dispatcher.handlerq, list)

    def test_dispatcher_dispatch(self):
        counts = dict(basic=0, general=0, test=0, error=0)
        dispatcher = self.create_dispatcher_with_handlers()
        for index in range(10):
            if index % 2 == 0:
                event = BasicEvent()
                counts['basic'] += 1
            elif index % 3 == 0:
                event = Event('general')
                counts['general'] += 1
            else:
                errdata = dict(error=index, message='{} is not divisible by 2 or 3'.format(index))
                event = ErrorEvent(data=errdata)
                counts['error'] += 1
            dispatcher.dispatch_events(event)
        for key in counts.keys():
            if key not in self.stats:
                self.stats[key] = 0
            self.assertEquals(counts[key], self.stats[key])
        for key in self.stats.keys():
            self.assertIn(key, counts)
        print('stats={}', self.stats)
        print('counts={}', counts)
