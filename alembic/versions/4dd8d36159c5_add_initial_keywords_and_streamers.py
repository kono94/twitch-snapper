"""add initial keywords and streamers

Revision ID: 4dd8d36159c5
Revises: 59a672baca4b
Create Date: 2023-11-12 23:14:42.091158

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4dd8d36159c5"
down_revision: Union[str, None] = "59a672baca4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """INSERT INTO `keyword` (`id`, `value`, `image_url`)
                                    VALUES
                                    (1, 'LUL', 'https://cdn.frankerfacez.com/emoticon/143984/4'),
                                    (2, 'OMEGALUL', 'https://cdn.frankerfacez.com/emoticon/128054/4'),
                                    (3, 'KEKW', 'https://cdn.frankerfacez.com/emoticon/381875/4'),
                                    (4, 'Pog', 'https://cdn.frankerfacez.com/emoticon/210748/4'),
                                    (5, 'PepeHands', 'https://cdn.frankerfacez.com/emoticon/231552/4'),
                                    (6, 'widepeepoHappy', 'https://cdn.frankerfacez.com/emoticon/270930/4'),
                                    (7, 'Pepega', 'https://cdn.frankerfacez.com/emoticon/243789/4'),
                                    (8, 'monkaW', 'https://cdn.frankerfacez.com/emoticon/214681/4'),
                                    (9, '5Head', 'https://cdn.frankerfacez.com/emoticon/239504/4'),
                                    (10, 'POGGERS', 'https://cdn.frankerfacez.com/emoticon/214129/4'),
                                    (11, 'monkaS ', 'https://cdn.frankerfacez.com/emoticon/130762/4'),
                                    (12, 'AYAYA', 'https://cdn.frankerfacez.com/emoticon/162146/4'),
                                    (13, 'PepeLaugh', 'https://cdn.frankerfacez.com/emoticon/64785/4'),
                                    (14, 'Sadge', 'https://cdn.frankerfacez.com/emoticon/425196/4'),
                                    (15, 'EZ', 'https://cdn.betterttv.net/emote/5590b223b344e2c42a9e28e3/3x.webp'),
                                    (16, 'PogU', 'https://cdn.betterttv.net/emote/5e4e7a1f08b4447d56a92967/3x.webp'),
                                    (17, 'PauseChamp', 'https://cdn.betterttv.net/emote/5cd6b08cf1dac14a18c4b61f/3x.webp'),
                                    (18, 'BOOBA', 'https://cdn.betterttv.net/emote/5fa99424eca18f6455c2bca5/3x.webp'),
                                    (19, 'monkaTOS', 'https://cdn.betterttv.net/emote/5a7fd054b694db72eac253f4/3x.webp');
                                    """
    )
    pass


def downgrade() -> None:
    pass
