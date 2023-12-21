import asyncio

from sqlalchemy import text

from snapper.database import TransactionHandler


async def seed_db():
    async with TransactionHandler.get_engine().connect() as conn:
        await conn.execute(
            text(
                """INSERT INTO `stream` (`id`, `channel_name`, `broadcaster_id`, `pause_interval`, `activation_time_window`, `activation_threshold`, `trigger_threshold`, `min_trigger_pause`, `created`, `updated`)
                                 VALUES
                                (1, 'lirik', '23161357', 3, 15, 4, 5, 10, '2023-10-07 20:12:24', '2023-10-07 20:12:24'),
                                (2, 'tarik', '36340781', 3, 15, 4, 5, 10, '2023-10-07 20:12:24', '2023-10-07 20:12:24'),
                                (3, 'zackrawrr', '552120296', 3, 15, 4, 5, 10, '2023-10-07 20:12:24', '2023-10-07 20:12:24');
                                """
            )
        )
        await conn.execute(
            text(
                """INSERT INTO `clip` (`id`, `twitch_clip_id`, `stream_id`, `keyword_id`, `thumbnail_url`, `title`, `view_count`, `keyword_count`, `created`)
                                VALUES
                                (1, 'OnerousProudRadicchioBabyRage-w-z15J3E7rXR8pAF', 1, 2, 'https://clips-media-assets2.twitch.tv/gm_ofcPs9eSdxO610fKQBQ/42876065515-offset-5206-preview-480x272.jpg', 'WOOP WOOP - Twitter @tarik', 7, 19, '2023-10-07 20:12:46'),
                                (2, 'SlickOilySamosaPhilosoraptor-krhB7dXpz2rhSOtp', 1, 3, 'https://clips-media-assets2.twitch.tv/Liy91pK4Qe3V6c9q4UjraQ/42875542523-offset-14936-preview-480x272.jpg', 'Forza into Party Animals - !CS2 - !MATRIX', 1, 7, '2023-10-07 20:13:55'),
                                (3, 'FreezingUnusualPenguinPartyTime-fuzoVyt_XSTUWGZu', 1, 3, 'https://clips-media-assets2.twitch.tv/BdL16H7s6Fcrf10k1Fhmbg/42875542523-offset-15030-preview-480x272.jpg', 'Forza into Party Animals - !CS2 - !MATRIX', 1, 29, '2023-10-07 20:15:29'),
                                (4, 'FaintRichGrasshopperLitty-IPosr_rszPMjoAjJ', 1, 3, 'https://clips-media-assets2.twitch.tv/7_cexiD6LK_67MzzI6AIyQ/42875542523-offset-15062-preview-480x272.jpg', 'Forza into Party Animals - !CS2 - !MATRIX', 1, 9, '2023-10-07 20:16:00');"""
            )
        )
        await conn.commit()


if __name__ == "__main__":
    asyncio.run(seed_db())
