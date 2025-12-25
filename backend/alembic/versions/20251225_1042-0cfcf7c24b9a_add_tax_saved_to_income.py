"""add_tax_saved_to_income

Revision ID: 0cfcf7c24b9a
Revises: 918f0ef7149f
Create Date: 2025-12-25 10:42:12.479868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cfcf7c24b9a'
down_revision = '918f0ef7149f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tax_saved column to incomes table
    op.add_column('incomes', sa.Column('tax_saved', sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade() -> None:
    # Remove tax_saved column from incomes table
    op.drop_column('incomes', 'tax_saved')
