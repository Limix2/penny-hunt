"""add store_cookie column and populate Walmart store cookies

Revision ID: 0001_store_cookie
Revises:
Create Date: 2026-05-30
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_store_cookie"
down_revision = None
branch_labels = None
depends_on = None

# Walmart store numbers -> cookie value is f"assortment={num}"
_WM_NUMBERS = ["5165", "429", "5809", "3886", "397", "452", "2763", "1041", "395"]


def upgrade():
    with op.batch_alter_table("stores") as batch:
        batch.add_column(sa.Column("store_cookie", sa.String(), nullable=True))
    for num in _WM_NUMBERS:
        op.execute(
            "UPDATE stores SET store_cookie='assortment=%s' "
            "WHERE chain='Walmart' AND store_code LIKE '%%%s%%'" % (num, num)
        )


def downgrade():
    with op.batch_alter_table("stores") as batch:
        batch.drop_column("store_cookie")
