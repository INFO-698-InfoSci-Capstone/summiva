from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys
import os
from pathlib import Path

# Fix import path to correctly find the settings module
project_root = Path(__file__).parent.parent.parent.parent.parent
config_dir = project_root / 'config'
settings_dir = config_dir / 'settings'

# Add to sys.path if not already there
for path in [str(project_root), str(config_dir), str(settings_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Create config directories if they don't exist (for Docker environments)
for path in [config_dir, settings_dir]:
    if not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"Created missing directory: {path}")
        except Exception as e:
            print(f"Warning: Could not create directory {path}: {str(e)}")

    # Create __init__.py files in config directories
    init_file = path / '__init__.py'
    if not init_file.exists() and path.exists():
        try:
            init_file.touch()
            print(f"Created __init__.py in {path}")
        except Exception as e:
            print(f"Warning: Could not create __init__.py in {path}: {str(e)}")

# Try different import approaches
try:
    from config.settings import settings
except ImportError:
    try:
        sys.path.insert(0, str(settings_dir))
        from settings import settings
    except ImportError as e:
        # Create a more comprehensive default settings class
        print(f"Warning: Could not import settings, using defaults: {str(e)}")
        class DefaultSettings:
            def __init__(self):
                # Database settings
                self.DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
                self.ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
                
                # Application settings
                self.APP_NAME = os.environ.get("APP_NAME", "Summiva")
                self.APP_SERVICE_VERSION = os.environ.get("APP_SERVICE_VERSION", "1.0.0")
                self.DEBUG = os.environ.get("DEBUG", "True") == "True"
                
                # CORS settings
                self.CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
                self.CORS_ALLOW_CREDENTIALS = os.environ.get("CORS_ALLOW_CREDENTIALS", "True") == "True"
                self.CORS_ALLOW_METHODS = ["*"]
                self.CORS_ALLOW_HEADERS = ["*"]
                
                # Redis settings for caching (if used)
                self.REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
                
            def __getattr__(self, name):
                # For any setting that's not defined, return None and log a warning
                print(f"Warning: Accessing undefined setting '{name}'")
                env_value = os.environ.get(name)
                if env_value:
                    print(f"Using environment value for {name}: {env_value}")
                    return env_value
                return None
                
        settings = DefaultSettings()

# Get environment-specific database connection parameters
def get_db_config():
    """Get database connection parameters based on environment"""
    # Basic config present in all environments
    db_config = {
        'pool_pre_ping': True,
        'pool_recycle': 1800,
    }
    
    # Environment-specific configurations
    if hasattr(settings, 'ENVIRONMENT'):
        if settings.ENVIRONMENT == "production":
            db_config.update({
                'pool_size': 20,
                'max_overflow': 40,
                'pool_timeout': 60,
            })
        elif settings.ENVIRONMENT == "staging":
            db_config.update({
                'pool_size': 10,
                'max_overflow': 20,
                'pool_timeout': 45,
            })
        else:  # development and testing
            db_config.update({
                'pool_size': 5,
                'max_overflow': 10,
                'pool_timeout': 30,
            })
    else:
        # Default to development settings if ENVIRONMENT is not defined
        db_config.update({
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
        })
        
    return db_config

# Create SQLAlchemy engine with environment-specific configuration
try:
    if hasattr(settings, 'DATABASE_URL'):
        engine = create_engine(
            str(settings.DATABASE_URL),
            **get_db_config()
        )
    else:
        # Fallback to SQLite if DATABASE_URL is not in settings
        sqlite_path = "sqlite:///./test.db"
        print(f"Warning: No DATABASE_URL found in settings. Using SQLite: {sqlite_path}")
        engine = create_engine(sqlite_path, **get_db_config())
except Exception as e:
    print(f"Error creating database engine: {str(e)}")
    print(f"Falling back to in-memory SQLite database")
    engine = create_engine("sqlite:///./test.db", **get_db_config())

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with all models"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise