# Contributing to Summiva

## Getting Started

### Prerequisites
- Python 3.8+
- Flutter SDK 3.0+
- Docker & Docker Compose
- Git

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/your-org/summiva.git
cd summiva
```

2. Set up Python environment:
```bash
cd src/backend
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install poetry
poetry install
```

3. Set up Flutter environment:
```bash
cd src/frontend
flutter pub get
```

4. Set up environment variables:
```bash
cp config/development/.env.template config/development/.env
# Edit .env with your local configuration
```

5. Start development services:
```bash
docker-compose -f infra/docker-compose.dev.yml up -d
```

## Development Workflow

### Branch Naming Convention
- Feature: `feature/description`
- Bugfix: `fix/description`
- Hotfix: `hotfix/description`
- Release: `release/version`

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

### Pull Request Process

1. Create a new branch from `develop`
2. Make your changes
3. Write/update tests
4. Update documentation
5. Run linters and tests
6. Create a pull request
7. Wait for review and approval

### Testing

#### Backend Tests
```bash
cd src/backend
poetry run pytest
```

#### Frontend Tests
```bash
cd src/frontend
flutter test
```

### Code Style

#### Backend
- Follow PEP 8
- Use Black for formatting
- Use isort for import sorting
- Use mypy for type checking

#### Frontend
- Follow Flutter style guide
- Use flutter_lints
- Run `flutter analyze`

## Release Process

1. Create release branch
2. Update version numbers
3. Update CHANGELOG.md
4. Create pull request to main
5. After approval and merge:
   - Tag the release
   - Push to production

## Documentation

- Update API documentation when endpoints change
- Keep README.md up to date
- Document new features
- Update configuration examples

## Security

- Never commit secrets
- Use environment variables
- Follow security best practices
- Report security issues privately

## Questions?

- Create an issue
- Contact the maintainers
- Check existing documentation 