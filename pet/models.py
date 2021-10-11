from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Boolean,
    DECIMAL,
    DateTime,
    ForeignKey,
)

from db import metadata

pet_table = Table(
    "pet",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", String(36), index=True, unique=True),
    Column("name", String(60)),
    Column("species", String(60)),
    Column("breed", String(60)),
    Column("age", Integer),
    Column("store", Integer, ForeignKey("store.id")),
    Column("price", DECIMAL(precision=10, scale="2")),
    Column("sold", Boolean, index=True, server_default="f"),
    Column("received_date", DateTime(timezone=True)),
    Column("sold_date", DateTime(timezone=True)),
    Column("live", Boolean, index=True, server_default="t"),
)
