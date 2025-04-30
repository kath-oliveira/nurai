import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

# Use the actual application's models
# Assuming your Flask app object is named 'app' and models are defined in 'app.py'
# You might need to adjust the import path based on your project structure
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
try:
    from app import db # Import db instance from your app
    target_metadata = db.metadata
except ImportError as e:
    print(f"Error importing app or db: {e}")
    print("Ensure your Flask app and SQLAlchemy db instance are correctly defined and importable.")
    target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url():
    # Get URL STRICTLY from environment variable
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable not set or empty. Cannot configure database.")

    # Heroku uses postgres:// but SQLAlchemy needs postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url() # Will raise ValueError if DATABASE_URL is not set
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get the actual database URL (will raise ValueError if not set)
    db_url = get_url()

    # Create engine configuration dictionary
    engine_config = {
        "sqlalchemy.url": db_url
    }

    connectable = engine_from_config(
        engine_config, # Use the dictionary with the corrected URL
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# Ensure target_metadata is available before running migrations
if target_metadata is None:
    print("Target metadata not loaded. Cannot run migrations.")
else:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()

