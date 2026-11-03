"""add outbox claim/lease fields

Revision ID: c4a1e9d27b30
Revises: 9b2f7a61c8e4
Create Date: 2026-10-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4a1e9d27b30'
down_revision: Union[str, Sequence[str], None] = '9b2f7a61c8e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('webhooknotificationqueue', sa.Column('claimed_at', sa.DateTime(), nullable=True))
    op.add_column('webhooknotificationqueue', sa.Column('lease_expires_at', sa.DateTime(), nullable=True))
    op.add_column('webhooknotificationqueue', sa.Column('completed_at', sa.DateTime(), nullable=True))
    op.create_index(
        op.f('ix_webhooknotificationqueue_lease_expires_at'),
        'webhooknotificationqueue',
        ['lease_expires_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_webhooknotificationqueue_status'),
        'webhooknotificationqueue',
        ['status'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_webhooknotificationqueue_status'), table_name='webhooknotificationqueue')
    op.drop_index(op.f('ix_webhooknotificationqueue_lease_expires_at'), table_name='webhooknotificationqueue')
    op.drop_column('webhooknotificationqueue', 'completed_at')
    op.drop_column('webhooknotificationqueue', 'lease_expires_at')
    op.drop_column('webhooknotificationqueue', 'claimed_at')
