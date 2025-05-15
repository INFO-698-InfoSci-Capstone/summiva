# migrations/env.py

from dotenv import load_dotenv
import os

from alembic import context
from sqlalchemy import create_engine, pool

# Load environment variables
load_dotenv()

# Fetch database connection parameters
postgres_user = os.getenv("POSTGRES_USER", "summiva_user")
postgres_password = os.getenv("POSTGRES_PASSWORD", "summiva_pass")
postgres_db = os.getenv("POSTGRES_DB", "summiva_db")
postgres_host = os.getenv("POSTGRES_HOST", "postgres") 
postgres_port = os.getenv("POSTGRES_PORT", "5432")

# Construct the database URL properly
database_url = os.getenv("DATABASE_URL")
if not database_url:
    database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    print(f"Using constructed database URL: {database_url}")

# Override sqlalchemy.url in Alembic config dynamically
config = context.config
config.set_main_option('sqlalchemy.url', database_url)

# Now continue Alembic setup (target_metadata, run_migrations, etc.)
