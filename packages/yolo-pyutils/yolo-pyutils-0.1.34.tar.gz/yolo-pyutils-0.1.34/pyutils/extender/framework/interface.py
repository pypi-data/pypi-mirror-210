from abc import ABC, abstractmethod
from pyutils.scheduling import event_driven


class Component(ABC):

    @abstractmethod
    def start(self): pass

    @abstractmethod
    def stop(self): pass


class Service(event_driven.Handler, Component, ABC):

    # return True means this service was reinitialized successfully, otherwise return False or None
    @abstractmethod
    def reinitialize(self, init_args):
        pass


# Command interface defines the required functions for concrete commands
class Command(ABC):

    def __init__(self, key, context):
        self.key = key
        self.context = context

    @abstractmethod
    def run(self, run_args):
        pass
