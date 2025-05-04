# Summiva Module Structure Guidelines

## Overview

This document outlines the standard module structure and import practices for the Summiva project to ensure consistency and avoid import-related issues.

## Project Structure

Summiva follows a service-oriented architecture with these key components:

```
summiva/
├── config/           # Configuration files
├── data/             # Data files
├── docs/             # Documentation
├── src/
│   ├── backend/      # Backend services
│   │   ├── auth/     # Authentication service
│   │   ├── core/     # Core shared modules
│   │   ├── grouping/ # Document grouping service
│   │   ├── search/   # Search service
│   │   ├── summarization/ # Summarization service
│   │   └── tagging/  # Document tagging service
│   └── frontend/     # Frontend code
└── tests/            # Tests
```

## Standard Import Paths

### 1. Always Use Absolute Imports

Use absolute imports starting from the project root:

```python
# Good
from backend.core.database.database import get_db
from config.settings.settings import settings

# Avoid
from ...core.database.database import get_db  # Relative imports are fragile
from src.backend.core.database.database import get_db  # Don't include src in path
```

### 2. Use the Import Helper

All modules should use the import helper at the top of the file:

```python
from backend.core.imports import setup_imports
setup_imports()

# Rest of your imports here
```

### 3. Standard Service Module Structure

Each service follows this structure:

```
service_name/
├── __init__.py       # Service package initialization
├── main.py           # Service entry point 
├── api/              # API routes
├── models/           # Database models
├── schemas/          # Pydantic schemas
├── utils/            # Utility functions
└── core/             # Service-specific core functionality
```

### 4. Service Initialization

Use the standard service initialization pattern:

```python
from backend.core.service_init import init_service

app = init_service(
    service_name="your_service_name",
    # Other configuration options
)
```

## Handling Circular Imports

If you encounter circular imports:

1. Use function-level imports for problematic modules
2. Use the `resolve_circular_imports` decorator:

```python
from backend.core.imports import resolve_circular_imports

@resolve_circular_imports
def get_user_model():
    from backend.auth.models import User
    return User
```

## Configuration Access

Always access settings through the standard settings object:

```python
from config.settings.settings import settings

# Then use settings.ATTRIBUTE_NAME
database_url = settings.DATABASE_URL
```

## Logging Setup

Use the standard logging setup:

```python
from config.logs.logging import setup_logging

logger = setup_logging("service_name")
# Or for submodules:
logger = setup_logging("service_name.submodule")
```

## Tools for Import Analysis

If you're unsure about import paths, use these utilities:

```python
from config.settings.module_paths import get_import_path, get_module_path

# Convert a file path to import notation
import_path = get_import_path("/path/to/file.py")

# Get file path from import notation
module_path = get_module_path("backend.auth.models")
```

## Common Issues and Solutions

1. **ModuleNotFoundError**: Ensure the module is in sys.path
2. **ImportError**: Check for circular dependencies
3. **Inconsistent imports**: Use the standard import path conventions

By following these guidelines, we maintain a consistent, maintainable codebase with predictable import behavior.