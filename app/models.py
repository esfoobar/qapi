from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)

from db import metadata


app_table = Table(
    "app",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(80), index=True, unique=True),
    Column("secret", String(87)),
)

app_access_table = Table(
    "app_access",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("app_id", Integer, ForeignKey("app.id")),
    Column("token", String(36)),
    Column("expires", DateTime(timezone=True)),
)
