import unittest
from pyutils.scheduling.event_driven import *


class ShareEvent(Event):
    def __init__(self, data):
        super().__init__(data)


class MarketEvent(Event):
    def __init__(self, data):
        super().__init__(data)


class ShareHandler(Handler):

    def __init__(self):
        self.data = list()

    def get_applicable_event_classes(self):
        return [ShareEvent]

    def get_data(self):
        return self.data

    def handle(self, event):
        self.data.append(event.get_data())


class ShareOrMarketHandler(ShareHandler):

    def get_applicable_event_classes(self):
        return [ShareEvent, MarketEvent]


class TestEventDriven(unittest.TestCase):

    def test_dispatch(self):
        dispatcher = Dispatcher()
        share_handler = ShareHandler()
        share_or_market_handler = ShareOrMarketHandler()

        # confirm that register non-event should raise error
        with self.assertRaises(RuntimeError) as err:
            dispatcher.register(ShareHandler, share_handler)
        self.assertTrue(err.exception.args[0].startswith("failed to register event type"))

        # confirm that register unsupported event should raise error
        with self.assertRaises(RuntimeError) as err:
            dispatcher.register(MarketEvent, share_handler)
        self.assertTrue(err.exception.args[0].startswith("unsupported event type"))

        # register events for handlers, then start dispatcher
        dispatcher.register(ShareEvent, share_handler)
        dispatcher.register(ShareEvent, share_or_market_handler)
        dispatcher.register(MarketEvent, share_or_market_handler)
        dispatcher.start()

        # dispatch two events, share event should be received by both handlers,
        # market event should only be received by share_or_market_handler.
        dispatcher.dispatch(ShareEvent("data1"))
        dispatcher.dispatch(MarketEvent("data2"))

        # stop dispatcher, and then waiting for all events to be processed
        dispatcher.stop()

        # confirm that share handler processed 1 event, another handler processed 2 events
        self.assertEqual(["data1"], share_handler.get_data())
        self.assertEqual(["data1", "data2"], share_or_market_handler.get_data())


if __name__ == '__main__':
    unittest.main()
