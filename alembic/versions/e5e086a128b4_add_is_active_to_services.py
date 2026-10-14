
"""Add is_active to services

Revision ID: e5e086a128b4
Revises: 30d5b87bcad3
Create Date: 2026-10-13 19:22:41.027729
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5e086a128b4'
down_revision: Union[str, Sequence[str], None] = '30d5b87bcad3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'services',
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('services', 'is_active')
