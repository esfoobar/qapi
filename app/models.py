from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime

from db import metadata


app_table = Table(
    "app",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Integer, primary_key=True),
    Column("secret", String(80)),
)

app_access_table = Table(
    "app_access",
    metadata,
    Column("app_id", Integer, ForeignKey("app.id")),
    Column("token", String(35)),
    Column("expires", DateTime(timezone=True)),
)
