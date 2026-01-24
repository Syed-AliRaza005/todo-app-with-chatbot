<%inherit file="//alembic/script.py.mako"/>
<%def name="format_down_revision(rev)">${repr(rev) if rev else "None"}</%def>
"""${message}

Revision ID: ${up_revision}
Revises: ${format_down_revision(down_revision)}
Create Date: ${create_date}

"""
from typing import Union
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
