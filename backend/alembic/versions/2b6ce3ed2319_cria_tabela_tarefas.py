"""cria tabela tarefas

Revision ID: 2b6ce3ed2319
Revises: 
Create Date: 2026-10-16 14:55:21.451267

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b6ce3ed2319'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'tarefas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.String(length=500), nullable=True),
        sa.Column('concluida', sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tarefas')
