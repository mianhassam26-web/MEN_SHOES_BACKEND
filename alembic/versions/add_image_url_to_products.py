"""Add image_url to products table

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-06-28

Yeh migration products table mein image_url column add karta hai.
Run karne ke liye: alembic upgrade head
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Products table mein image_url column add karo.
    nullable=True hai kyunki purane products ki image nahi hogi.
    """
    op.add_column(
        'products',
        sa.Column('image_url', sa.String(), nullable=True)
    )


def downgrade() -> None:
    """
    Agar rollback karna ho to yeh column hata do.
    """
    op.drop_column('products', 'image_url')
