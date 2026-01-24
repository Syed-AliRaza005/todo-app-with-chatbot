"""Add chat session and message tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-23

"""
from typing import Union
from alembic import op
import sqlalchemy as sa
import sqlmodel
import uuid


# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create chatsession table
    op.create_table(
        "chatsession",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    )

    # Create chatmessage table
    op.create_table(
        "chatmessage",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("sender", sa.String(50), nullable=False, default="user"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, default="sent"),
        sa.ForeignKeyConstraint(["session_id"], ["chatsession.id"], ondelete="CASCADE"),
    )

    # Create indexes for chat tables
    op.create_index("ix_chatsession_user_id", "chatsession", ["user_id"])
    op.create_index("ix_chatsession_status", "chatsession", ["status"])
    op.create_index("ix_chatsession_created_at", "chatsession", ["created_at"])
    op.create_index("ix_chatmessage_session_id", "chatmessage", ["session_id"])
    op.create_index("ix_chatmessage_timestamp", "chatmessage", ["timestamp"])
    op.create_index("ix_chatmessage_sender", "chatmessage", ["sender"])


def downgrade() -> None:
    op.drop_index("ix_chatmessage_sender", table_name="chatmessage")
    op.drop_index("ix_chatmessage_timestamp", table_name="chatmessage")
    op.drop_index("ix_chatmessage_session_id", table_name="chatmessage")
    op.drop_index("ix_chatsession_created_at", table_name="chatsession")
    op.drop_index("ix_chatsession_status", table_name="chatsession")
    op.drop_index("ix_chatsession_user_id", table_name="chatsession")
    op.drop_table("chatmessage")
    op.drop_table("chatsession")