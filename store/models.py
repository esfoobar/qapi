from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Boolean,
)

from db import metadata

store_table = Table(
    "store",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", String(36), index=True, unique=True),
    Column("neighborhood", String(255)),
    Column("street_address", String(255)),
    Column("city", String(80)),
    Column("state", String(2)),
    Column("zip_code", String(5)),
    Column("phone", String(20)),
    Column("live", Boolean, index=True, server_default="t"),
)
