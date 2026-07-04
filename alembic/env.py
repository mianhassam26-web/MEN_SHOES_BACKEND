# ========================================
# alembic/env.py - Migration Environment
# ========================================

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ----------------------------------------
# Project root ko Python path mein add karo
# Taake 'app' folder mil sake
# ----------------------------------------
# Yeh file alembic/ folder mein hai
# os.path.dirname(__file__) = alembic/ folder
# .. = ek upar = project root (jahan app/ folder hai)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# .env file load karo
from dotenv import load_dotenv
load_dotenv()

# ----------------------------------------
# Hamare Models Import Karo
# ----------------------------------------
from app.database.database import Base
from app.models.models import User, Category, Product, Cart, CartItem, Order, OrderItem

# Alembic config object
config = context.config

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ----------------------------------------
# DATABASE URL - .env se lo
# ----------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Target metadata - haare models ki info
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Offline mode - sirf SQL generate karo"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Online mode - seedha Neon database mein tables banao"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Neon ke liye NullPool best hai
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


# Offline ya Online decide karo
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
