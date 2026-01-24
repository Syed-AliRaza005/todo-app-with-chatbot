"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-01-03

"""
from typing import Union
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "user",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    # Create tasks table with foreign key
    op.create_table(
        "task",
        sa.Column("id", sa.UUID(), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="Pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    )

    # Create revoked_tokens table
    op.create_table(
        "revokedtoken",
        sa.Column("token_jti", sa.String(255), primary_key=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    )

    # Create indexes
    op.create_index("ix_task_user_id", "task", ["user_id"])
    op.create_index("ix_task_status", "task", ["status"])
    op.create_index("ix_revokedtoken_expires", "revokedtoken", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_revokedtoken_expires", table_name="revokedtoken")
    op.drop_index("ix_task_status", table_name="task")
    op.drop_index("ix_task_user_id", table_name="task")
    op.drop_table("revokedtoken")
    op.drop_table("task")
    op.drop_table("user")
