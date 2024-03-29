"""Initial migration

Revision ID: bc53b3eb3893
Revises:
Create Date: 2023-08-13 14:38:34.498372

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bc53b3eb3893"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "clips",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("clip_id", sa.String(length=255), nullable=True),
        sa.Column("channel_name", sa.String(length=255), nullable=True),
        sa.Column("keyword_trigger", sa.String(length=255), nullable=True),
        sa.Column("keyword_count", sa.Integer(), nullable=True),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("clips")
    # ### end Alembic commands ###
