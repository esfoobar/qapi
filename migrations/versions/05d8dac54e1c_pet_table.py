"""pet table

Revision ID: 05d8dac54e1c
Revises: cedfd166c8c7
Create Date: 2021-10-11 20:55:03.604773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "05d8dac54e1c"
down_revision = "cedfd166c8c7"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "pet",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uid", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=60), nullable=True),
        sa.Column("species", sa.String(length=60), nullable=True),
        sa.Column("breed", sa.String(length=60), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("store_id", sa.Integer(), nullable=True),
        sa.Column("price", sa.DECIMAL(precision=10, scale="2"), nullable=True),
        sa.Column("sold", sa.Boolean(), server_default="f", nullable=True),
        sa.Column("received_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sold_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("live", sa.Boolean(), server_default="t", nullable=True),
        sa.ForeignKeyConstraint(
            ["store_id"],
            ["store.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pet_live"), "pet", ["live"], unique=False)
    op.create_index(op.f("ix_pet_sold"), "pet", ["sold"], unique=False)
    op.create_index(op.f("ix_pet_uid"), "pet", ["uid"], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_pet_uid"), table_name="pet")
    op.drop_index(op.f("ix_pet_sold"), table_name="pet")
    op.drop_index(op.f("ix_pet_live"), table_name="pet")
    op.drop_table("pet")
    # ### end Alembic commands ###