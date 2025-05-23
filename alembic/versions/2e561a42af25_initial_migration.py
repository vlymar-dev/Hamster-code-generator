"""Initial migration

Revision ID: 2e561a42af25
Revises:
Create Date: 2024-08-26 21:49:57.729265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '2e561a42af25'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###.
    op.create_table(
        'chain_cube_2048',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('promo_code', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
    )

    op.create_table(
        'merge_away',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('promo_code', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
    )

    op.create_table(
        'mow_and_trim',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('promo_code', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
    )

    op.create_table(
        'mud_racing',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('promo_code', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
    )

    op.create_table(
        'polysphere',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('promo_code', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
    )

    op.create_table(
        'train_miner',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('promo_code', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
    )

    op.create_table(
        'twerk_race_3d',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('promo_code', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chat_id', sa.BigInteger(), unique=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), unique=True, nullable=False),
        sa.Column('first_name', sa.String(length=100)),
        sa.Column('last_name', sa.String(length=100)),
        sa.Column('username', sa.String(length=100)),
        sa.Column('registration_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('language_code', sa.String(length=10)),
        sa.Column('preferred_currency', sa.String(length=3)),
        sa.Column('is_banned', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('user_status', sa.String(length=20), nullable=False, server_default=sa.text("'free'")),
        sa.Column('user_role', sa.String(length=20), nullable=False, server_default=sa.text("'user'")),
        sa.Column('referral_code', sa.String(length=50)),
        sa.Column('referred_by', sa.String(length=50)),
        sa.Column('is_subscribed', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('daily_requests_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('last_reset_date', sa.Date(), nullable=False, server_default=sa.text("now()::date")),
        sa.Column('last_request_time', sa.DateTime(timezone=True)),
        sa.Column('total_keys_generated', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('notes', sa.Text()),
    )

    op.create_table(
        'user_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('action', sa.Text()),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_logs')
    op.drop_table('users')
    op.drop_table('twerk_race_3d')
    op.drop_table('train_miner')
    op.drop_table('polysphere')
    op.drop_table('mud_racing')
    op.drop_table('mow_and_trim')
    op.drop_table('merge_away')
    op.drop_table('chain_cube_2048')
    # ### end Alembic commands ###
