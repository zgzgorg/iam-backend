from logging.config import fileConfig

from alembic import context

import zgiam.core
import zgiam.database
import zgiam.models


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = zgiam.models.base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    zgiam.database.get_db()  # Load SQLALCHEMY_DATABASE_URI to config
    url = zgiam.core.get_app().config["SQLALCHEMY_DATABASE_URI"]

    # add `render_as_batch` due to
    # https://alembic.sqlalchemy.org/en/latest/batch.html#batch-mode-with-autogenerate
    # and https://stackoverflow.com/q/30378233/9604912

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = zgiam.database.get_db().get_engine()

    with connectable.connect() as connection:
        # add `render_as_batch` due to
        # https://alembic.sqlalchemy.org/en/latest/batch.html#batch-mode-with-autogenerate
        # and https://stackoverflow.com/q/30378233/9604912
        context.configure(
            connection=connection, target_metadata=target_metadata, render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
