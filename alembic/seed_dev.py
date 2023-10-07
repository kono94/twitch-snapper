import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

from snapper.database import engine


async def seed_db():
    async with engine.connect() as conn:
        await conn.execute(
            text(
                """INSERT INTO `stream` (`id`, `channel_name`, `broadcaster_id`, `keyword_list`, `pause_interval`, `activation_time_window`, `activation_threshold`, `trigger_threshold`, `min_trigger_pause`, `created`, `updated`)
                                 VALUES
                                (1, 'lirik', '23161357', 'KEK,OWO,LUL', 3, 15, 4, 5, 10, '2023-10-07 20:12:24', '2023-10-07 20:12:24'),
                                (2, 'tarik', '36340781', 'KEK,OWO,LUL', 3, 15, 4, 5, 10, '2023-10-07 20:12:24', '2023-10-07 20:12:24'),
                                (3, 'zackrawrr', '552120296', 'KEK,OWO,LUL', 3, 15, 4, 5, 10, '2023-10-07 20:12:24', '2023-10-07 20:12:24');
                                """
            )
        )
        await conn.execute(
            text(
                """INSERT INTO `clip` (`id`, `twitch_clip_id`, `stream_id`, `keyword_trigger`, `keyword_count`, `created`)
                                VALUES
                                (1, 'OnerousProudRadicchioBabyRage-w-z15J3E7rXR8pAF', 2, 'KEK', 7, '2023-10-07 20:12:46'),
                                (2, 'SlickOilySamosaPhilosoraptor-krhB7dXpz2rhSOtp', 1, 'KEK', 7, '2023-10-07 20:13:55'),
                                (3, 'FreezingUnusualPenguinPartyTime-fuzoVyt_XSTUWGZu', 1, 'KEK', 29, '2023-10-07 20:15:29'),
                                (4, 'FaintRichGrasshopperLitty-IPosr_rszPMjoAjJ', 1, 'KEK', 9, '2023-10-07 20:16:00');"""
            )
        )
        await conn.commit()


if __name__ == "__main__":
    asyncio.run(seed_db())
