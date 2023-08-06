from abc import ABC, abstractmethod
from threading import Thread
import queue
import logging


class Dispatcher:

    def __init__(self, name="default"):
        self.__name = name
        self._mapping = dict()
        self._running = False
        self._thread = Thread(target=self.handle, args=())
        self._queue = queue.Queue()
        self._done = object()

    def start(self):
        self._running = True
        self._thread.start()
        logging.info("dispatcher {} started".format(self.__name))

    def stop(self):
        if self._running:
            self._queue.put(self._done)
            # Wait for actual termination
            self._thread.join()
            logging.info("dispatcher {} stopped".format(self.__name))
        else:
            logging.info("skip stopping dispatcher {} which is already stopped".format(self.__name))

    def register(self, event_class, handler):
        if not issubclass(event_class, Event):
            raise RuntimeError("[dispatcher {}] failed to register event type {0}".format(self.__name, event_class))
        if event_class not in handler.get_applicable_event_classes():
            raise RuntimeError("[dispatcher {}] unsupported event type {} for handler {}".format(
                self.__name, event_class, type(handler)))
        handlers = self._mapping.get(event_class)
        if handlers is None:
            handlers = [handler]
            self._mapping[event_class] = handlers
        else:
            handlers.append(handler)
        logging.info("[dispatcher {}] registered event_class {} with {} handlers: {}".format(
            self.__name, event_class, len(handlers), handlers))

    def unregister(self, event_class, handler):
        handlers = self._mapping.get(event_class)
        if handlers is not None:
            for existing_handler in handlers:
                if existing_handler == handler:
                    handlers.remove(existing_handler)
                    logging.info("[dispatcher {}] removed handler {} from event {}"
                                 .format(self.__name, existing_handler, event_class))

    def dispatch(self, event):
        self._queue.put(event)
        if self._queue.qsize() % 100 == 0:
            logging.info("[dispatcher {}] dispatch event {}, queue size: {}".format(
                self.__name, type(event), self._queue.qsize()))

    def handle(self):
        logging.info("[dispatcher {}] handle thread started!".format(self.__name))
        while self._running:
            event = self._queue.get()
            if event is self._done:
                break
            key = type(event)
            handlers = self._mapping.get(key)
            if handlers is None:
                raise RuntimeError("[dispatcher {}] failed to find handler for event type {}".format(
                    self.__name, type(event)))
            for handler in handlers:
                try:
                    handler.handle(event)
                except Exception as ex:
                    logging.error("[dispatcher {}] failed to handle event {}".format(self.__name, type(event)), ex)
            logging.debug("[dispatcher {}] processed event {}, queue size: {}".format(
                self.__name, event, self._queue.qsize()))
        logging.info("[dispatcher {}] handle thread stopped!!".format(self.__name))


class Event(ABC):

    def __init__(self, data=None):
        self.data = data

    def get_data(self):
        return self.data


class Handler(ABC):

    @abstractmethod
    def get_applicable_event_classes(self): pass

    @abstractmethod
    def handle(self, event): pass
