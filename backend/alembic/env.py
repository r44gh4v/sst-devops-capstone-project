from logging.config import fileConfig

from alembic import context
from sqlalchemy import text

from app.db import Base, engine
from app import models  # noqa: F401

fileConfig(context.config.config_file_name)

with engine.connect() as connection:
    if connection.dialect.name == "postgresql":
        connection.execute(text("SELECT pg_advisory_lock(1)"))
        connection.commit()
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
