import logging

from twitchAPI.twitch import Twitch
from twitchAPI.types import AuthScope

from snapper.util import get_env_variable

Log = logging.getLogger(__name__)


class TwitchApiHandler:
    _instance = None  # Class variable to hold the singleton instance

    @classmethod
    async def init_twitchAPI(cls) -> Twitch:
        if cls._instance is None:
            twitch = await Twitch(
                get_env_variable("TWITCH_APP_ID"),
                get_env_variable("TWITCH_APP_SECRET"),
            )
            Log.debug("Logged into twitch")
            target_scope = [AuthScope.CLIPS_EDIT]
            token = get_env_variable("TWITCH_CLIENT_TOKEN")
            refresh_token = get_env_variable("TWITCH_CLIENT_REFRESH_TOKEN")
            await twitch.set_user_authentication(token, target_scope, refresh_token)
            Log.debug("Set User Authentication")
            cls._instance = twitch  # Store the instance in the class variable
        return cls._instance
