"""add outbox idempotency fields

Revision ID: 9b2f7a61c8e4
Revises: 2db8b3141d33
Create Date: 2026-10-23 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b2f7a61c8e4'
down_revision: Union[str, Sequence[str], None] = '2db8b3141d33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('webhooknotificationqueue', sa.Column('source_event_id', sa.String(), nullable=True))
    op.add_column('webhooknotificationqueue', sa.Column('event_created', sa.DateTime(), nullable=True))
    op.add_column('webhooknotificationqueue', sa.Column('notification_key', sa.String(), nullable=True))
    op.create_index(op.f('ix_webhooknotificationqueue_source_event_id'), 'webhooknotificationqueue', ['source_event_id'], unique=False)
    op.create_index(op.f('ix_webhooknotificationqueue_notification_key'), 'webhooknotificationqueue', ['notification_key'], unique=False)
    with op.batch_alter_table('webhooknotificationqueue') as batch_op:
        batch_op.create_unique_constraint(
            'uq_webhooknotificationqueue_notification_key',
            ['notification_key']
        )


def downgrade() -> None:
    with op.batch_alter_table('webhooknotificationqueue') as batch_op:
        batch_op.drop_constraint(
            'uq_webhooknotificationqueue_notification_key',
            type_='unique'
        )
    op.drop_index(op.f('ix_webhooknotificationqueue_notification_key'), table_name='webhooknotificationqueue')
    op.drop_index(op.f('ix_webhooknotificationqueue_source_event_id'), table_name='webhooknotificationqueue')
    op.drop_column('webhooknotificationqueue', 'notification_key')
    op.drop_column('webhooknotificationqueue', 'event_created')
    op.drop_column('webhooknotificationqueue', 'source_event_id')
