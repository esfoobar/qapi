from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Boolean,
)

from db import metadata

pet_table = Table(
    "Pet",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", String(36), index=True, unique=True),
    Column("live", Boolean, index=True, server_default="t"),
)
