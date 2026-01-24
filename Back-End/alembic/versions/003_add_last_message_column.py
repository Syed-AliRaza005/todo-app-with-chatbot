"""Add last_message column to chatsession table

Revision ID: 003
Revises: 002
Create Date: 2026-01-23

"""
from typing import Union
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the last_message column to chatsession table
    op.add_column('chatsession', sa.Column('last_message', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove the last_message column from chatsession table
    op.drop_column('chatsession', 'last_message')