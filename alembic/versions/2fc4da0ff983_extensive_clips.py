"""extensive clips

Revision ID: 2fc4da0ff983
Revises: ed2720873766
Create Date: 2023-10-07 22:40:36.287861

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2fc4da0ff983"
down_revision: Union[str, None] = "ed2720873766"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "clip", sa.Column("twitch_clip_id", sa.String(length=255), nullable=False)
    )
    op.alter_column(
        "clip",
        "stream_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.alter_column(
        "clip",
        "keyword_trigger",
        existing_type=mysql.VARCHAR(length=255),
        nullable=False,
    )
    op.alter_column(
        "clip",
        "keyword_count",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=False,
    )
    op.alter_column(
        "clip",
        "created",
        existing_type=mysql.DATETIME(),
        nullable=False,
        existing_server_default=sa.text("current_timestamp()"),  # type: ignore
    )
    op.drop_column("clip", "clip_id")
    op.add_column("stream", sa.Column("pause_interval", sa.Integer(), nullable=False))
    op.add_column(
        "stream", sa.Column("activation_time_window", sa.Integer(), nullable=False)
    )
    op.add_column(
        "stream", sa.Column("activation_threshold", sa.Integer(), nullable=False)
    )
    op.add_column(
        "stream", sa.Column("trigger_threshold", sa.Integer(), nullable=False)
    )
    op.add_column(
        "stream", sa.Column("min_trigger_pause", sa.Integer(), nullable=False)
    )
    op.alter_column(
        "stream",
        "channel_name",
        existing_type=mysql.VARCHAR(length=255),
        nullable=False,
    )
    op.alter_column(
        "stream",
        "broadcaster_id",
        existing_type=mysql.VARCHAR(length=255),
        nullable=False,
    )
    op.alter_column(
        "stream",
        "keyword_list",
        existing_type=mysql.VARCHAR(length=1000),
        nullable=False,
    )
    op.alter_column(
        "stream",
        "created",
        existing_type=mysql.DATETIME(),
        nullable=False,
        existing_server_default=sa.text("current_timestamp()"),  # type: ignore
    )
    op.alter_column("stream", "updated", existing_type=mysql.DATETIME(), nullable=False)
    op.create_unique_constraint("broadcaster_id", "stream", ["broadcaster_id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("broadcaster_id", "stream", type_="unique")
    op.alter_column("stream", "updated", existing_type=mysql.DATETIME(), nullable=True)
    op.alter_column(
        "stream",
        "created",
        existing_type=mysql.DATETIME(),
        nullable=True,
        existing_server_default=sa.text("current_timestamp()"),  # type: ignore
    )
    op.alter_column(
        "stream",
        "keyword_list",
        existing_type=mysql.VARCHAR(length=1000),
        nullable=True,
    )
    op.alter_column(
        "stream",
        "broadcaster_id",
        existing_type=mysql.VARCHAR(length=255),
        nullable=True,
    )
    op.alter_column(
        "stream", "channel_name", existing_type=mysql.VARCHAR(length=255), nullable=True
    )
    op.drop_column("stream", "min_trigger_pause")
    op.drop_column("stream", "trigger_threshold")
    op.drop_column("stream", "activation_threshold")
    op.drop_column("stream", "activation_time_window")
    op.drop_column("stream", "pause_interval")
    op.add_column(
        "clip", sa.Column("clip_id", mysql.VARCHAR(length=255), nullable=True)
    )
    op.alter_column(
        "clip",
        "created",
        existing_type=mysql.DATETIME(),
        nullable=True,
        existing_server_default=sa.text("current_timestamp()"),  # type: ignore
    )
    op.alter_column(
        "clip",
        "keyword_count",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=True,
    )
    op.alter_column(
        "clip",
        "keyword_trigger",
        existing_type=mysql.VARCHAR(length=255),
        nullable=True,
    )
    op.alter_column(
        "clip",
        "stream_id",
        existing_type=mysql.INTEGER(display_width=11),
        nullable=True,
    )
    op.drop_column("clip", "twitch_clip_id")
    # ### end Alembic commands ###
