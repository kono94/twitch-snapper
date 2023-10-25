import logging
import unittest
from unittest.mock import AsyncMock, Mock, patch

from sqlalchemy import select
from twitchAPI.object import Clip as TwitchClip

from snapper.config import configure_environment, configure_logging
from snapper.database import Clip, Keyword, Stream, TransactionHandler
from snapper.observer import KeywordData, StreamObserver
from snapper.twitch import TwitchApiHandler

Log = logging.getLogger(__name__)


class TestSuit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        configure_environment(".env")
        configure_environment(".env.test")
        configure_logging()
        await TransactionHandler.drop_and_create_database()
        # Code that runs before each test method
        self.twitchAPI = await TwitchApiHandler.init_twitchAPI()
        Log.info("setup done")

    async def test_invoke_trigger(self):
        # Mock TwitchClip
        mock_twitch_clip = Mock(spec=TwitchClip)
        mock_twitch_clip.id = "69"
        mock_twitch_clip.thumbnail_url = "test.com"
        mock_twitch_clip.view_count = 420
        mock_twitch_clip.title = "title"

        test_keyword_data = KeywordData()
        test_keyword_data.count = 77

        test_keyword = Keyword(value="LUL", image_url="http://example.com/lul.png")
        test_stream = Stream("papaplatte", "50985620")
        test_stream.keywords.append(test_keyword)

        observer = StreamObserver(self.twitchAPI, test_stream)

        # Mocking _create_clip method that does post requests to TwitchAPI
        with patch(
            "snapper.observer.StreamObserver._create_clip",
            new=AsyncMock(return_value=mock_twitch_clip),
        ):
            await observer._invoke_trigger(test_keyword, test_keyword_data)

        # Verify that the Clip object was persisted
        async with TransactionHandler.create_new_async_session() as session:
            added_clip = (
                await session.execute(select(Clip).filter_by(twitch_clip_id="69"))
            ).first()
            print(added_clip)
            self.assertIsNotNone(added_clip)
