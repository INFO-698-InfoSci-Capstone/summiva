# migrations/env.py

from dotenv import load_dotenv
import os

from alembic import context
from sqlalchemy import create_engine, pool

# Load environment variables
load_dotenv()

# Fetch DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL")

# Override sqlalchemy.url in Alembic config dynamically
config = context.config
config.set_main_option('sqlalchemy.url', database_url)

# Now continue Alembic setup (target_metadata, run_migrations, etc.)
