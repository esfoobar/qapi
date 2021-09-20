"""creating store tables

Revision ID: cedfd166c8c7
Revises: 31eed0f89308
Create Date: 2021-09-20 18:04:07.905936

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cedfd166c8c7"
down_revision = "31eed0f89308"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "store",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uid", sa.String(length=36), nullable=True),
        sa.Column("neighborhood", sa.String(length=255), nullable=True),
        sa.Column("street_address", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=80), nullable=True),
        sa.Column("state", sa.String(length=2), nullable=True),
        sa.Column("zip_code", sa.String(length=5), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("live", sa.Boolean(), server_default="t", nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_store_live"), "store", ["live"], unique=False)
    op.create_index(op.f("ix_store_uid"), "store", ["uid"], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_store_uid"), table_name="store")
    op.drop_index(op.f("ix_store_live"), table_name="store")
    op.drop_table("store")
    # ### end Alembic commands ###
