import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.append(str(Path(__file__).resolve().parent.parent))

from snapper.app import init_twitchAPI
from snapper.observer import StreamObserver


class TestSuit:
    async def async_setup(self):
        self.twitchAPI = await init_twitchAPI()
        print("setup done")

    async def test_trigger(self):
        print("test_trigger")
        observer = StreamObserver("lirik", self.twitchAPI)
        await observer._create_clip("kek", 10)


class TestRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testSuit = TestSuit()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cls.testSuit.async_setup())

    def test_1(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.testSuit.test_trigger())


if __name__ == "__main__":
    unittest.main()
