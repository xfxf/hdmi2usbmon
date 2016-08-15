"""
    Generic event interface
    Part of hdmi2usbd
"""
from abc import ABCMeta, abstractmethod
import time
import six
# Fix for py2.x with `pip install future`
# noinspection PyCompatibility
import queue


class Event(object):
    """
    Event: container for an event
    records timestamp, event_type, and optionally data for the event
    """
    __slots__ = ('timestamp', 'event_type', 'data')
    DEFAULT_EVENT_TYPE = 'basic'

    def __init__(self, event_type=None, data=None, timestamp=None):
        if isinstance(event_type, Event):
            self.timestamp = event_type.timestamp
            self.event_type = event_type.event_type
            self.data = event_type.data
        else:
            event_type = Event.DEFAULT_EVENT_TYPE if event_type is None else event_type
            if isinstance(event_type, six.string_types):
                event_type = event_type.split(',')
            self.timestamp = time.time() if timestamp is None else timestamp
            self.data = data

    @staticmethod
    def create_event(event_type=None, data=None, timestamp=None, _class=None):
        """
        :param _class: class to use for the event (default=Event, must be Event sublcass)
        :param type: string to classify the event
        :param data: data related to the event
        :return: Event
        """
        if _class is None:
            _class = Event
        return _class(event_type=event_type, data=data, timestamp=timestamp)


class EventHandler(object):
    """
    Handler for an event
    On event dispatch, each handler is called in turn if its filter_event method returns True for the event
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def accept_event(self, event):
        """
        accept_event: return true if this handler should handle the event
        :param event:
        :return:
        """
        return False

    @abstractmethod
    def handle_event(self, event):
        """
        handle_event: handle an event - default implementation does nothing
        :param event: event to handle
        """
        pass


class EventTypeHandler(EventHandler):
    """
    Genmeric handler based on type and callable
    """
    def __init__(self, func, *types):
        self.func=func
        self.filter_only = list()
        for type in types:
            if isinstance(type, (list, tuple)):
                self.filter_only.extend(type)
            else:
                self.filter_only.append(type)

    def accept_event(self, event):
        if not self.filter_only:
            return True
        for event_type in event.event_type:
            if event_type in self.filter_only:
                return True
        return False

    def handle_event(self, event):
        return self.func(event)


class EventDispatcher(object):

    def __init__(self, qclass=queue.Queue, hclass=list):
        self.eventq = qclass()
        self.handlerq = hclass()

    def add_handler(self, handler, at_pos=None):
        """
        Add a (new) handler to the handler list
        :param handler: handler (must be EventHandler subclass)
        :param at_pos: None or False (default) - append, True = insert at start, integer = insert at position
        :return: True if handler was added, False otherwise
        """
        assert isinstance(handler, EventHandler)
        if not handler in self.handlerq:
            if not at_pos:
                self.handlerq.append(handler)
            elif at_pos is True:
                self.handlerq.insert(0, handler)
            else:
                self.handlerq.insert(int(at_pos), handler)
            return True
        return False

    def remove_handler(self, handler):
        """
        Remove an existing handler from the handler list
        :param handler: Handler to remove, None for all
        :return: True if handler was installed
        """
        if handler is None:
            self.handlerq.clear()
        elif handler in self.handlerq:
            assert issubclass(handler, EventHandler)
            del self.handlerq[self.handlerq.index(handler)]
        else:
            return False
        return True

    def send_event(self, event, block=True, timeout=None):
        """
        Add an event to the event queue
        :param event: event to queue
        note: blocks
        """
        if event is not None:
            assert isinstance(event, Event)
            try:
                self.eventq.put(event, block, timeout)
                return True
            except queue.Full as exc:
                pass
        return False

    def dispatch_events(self, *events, **kwargs):
        """
        Dispatch events in the queue
        :param events: zero or more events to add to the queue before dispatch
        :param loop: whether to keep looping over events (on timeout)
        :param block: require syncrhonous dispatch of all events in the queue
        :param timeout: wait timeout
        """
        loop = kwargs.get('loop', False)
        block = kwargs.get('block', True)
        timeout = kwargs.get('timeout', None)
        hcount = qcount = 0
        # queue additional events
        for event in events:
            if not self.send_event(event, block, timeout):
                break
            qcount += 1
        # dispatch events from the queue
        while loop or self.eventq.qsize() > 0:
            try:
                event = self.eventq.get(loop, timeout)
            except queue.Empty:
                continue
            for handler in tuple(self.handlerq):
                if handler.accept_event(event):
                    handler.handle_event(event)
                    hcount += 1
        return qcount, hcount
