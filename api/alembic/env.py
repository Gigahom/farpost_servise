from logging.config import fileConfig
from sqlalchemy import pool

from alembic import context
from src.settings.config import SQLALCHEMY_ASYNC_DATABASE_URL
from src.apps.models import Base

import asyncio

from sqlalchemy.ext.asyncio import async_engine_from_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

config.set_main_option("sqlalchemy.url", SQLALCHEMY_ASYNC_DATABASE_URL)
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
#
# exclude_tables = [
#     "geocode_settings_default",
#     "geocode_settings_default",
#     "geocode_settings",
#     "loader_platform",
#     "pagc_lex",
#     "zip_lookup_all",
#     "state",
#     "countysub_lookup",
#     "addrfeat",
#     "tabblock20",
#     "tabblock",
#     "zip_state",
#     "secondary_unit_lookup",
#     "zcta5",
#     "tract",
#     "zip_state_loc",
#     "faces",
#     "pagc_gaz",
#     "county_lookup",
#     "topology",
#     "pagc_rules",
#     "loader_variables",
#     "cousub",
#     "zip_lookup",
#     "county",
#     "place_lookup_state_idx",
#     "place_lookup",
#     "zip_lookup_base",
#     "edges",
#     "loader_lookuptables",
#     "street_type_lookup",
#     "state_lookup",
#     "layer",
#     "addr",
#     "place",
#     "bg",
#     "featnames",
#     "direction_lookup",
# ]

#
# def include_object(object, name, type_, *args, **kwargs):
#     if name not in exclude_tables:
#         return alembic_helpers.include_object(object, name, type_, *args, **kwargs)
#     return not (type_ == "table" and name in exclude_tables)


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # process_revision_directives=alembic_helpers.writer,
        # render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = SQLALCHEMY_ASYNC_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=False,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        # process_revision_directives=alembic_helpers.writer,
        # render_item=alembic_helpers.render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())