"""cria tabela items

Revision ID: 7c3f9a1d2e4b
Revises: 2b6ce3ed2319
Create Date: 2026-11-14 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c3f9a1d2e4b'
down_revision: Union[str, Sequence[str], None] = '2b6ce3ed2319'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=50), nullable=False),
        sa.Column('descricao', sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'uq_items_nome_lower', 'items', [sa.text('lower(nome)')], unique=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_items_nome_lower', table_name='items')
    op.drop_table('items')
