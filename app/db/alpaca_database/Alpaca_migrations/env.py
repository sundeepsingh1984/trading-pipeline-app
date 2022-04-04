from logging.config import fileConfig
import sys
import pathlib
import alembic
from sqlalchemy import engine_from_config
from sqlalchemy import pool
sys.path.append(str(pathlib.Path(__file__).resolve().parents[4]))

from alembic import context
import app.config as Config
from app.models.alpaca_db_models import Alpaca_Base

from logging.config import fileConfig
import logging

print(Config.DATABASE_URL_ALPACA)



# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

config = alembic.context.config

print(Config.DATABASE_URL_ALPACA)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Alpaca_Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Interpret the config file for logging
fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")







def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode
    """
    connectable = config.attributes.get("connection", None)
    config.set_main_option("sqlalchemy.url", str(Config.DATABASE_URL_ALPACA))



    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        
    with connectable.connect() as connection:
        alembic.context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with alembic.context.begin_transaction():
            alembic.context.run_migrations()


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    """
    alembic.context.configure(url=str(Config.DATABASE_URL_ALPACA))

    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


if alembic.context.is_offline_mode():
    logger.info("Running migrations offline")
    run_migrations_offline()
else:
    logger.info("Running migrations online")
    run_migrations_online()

