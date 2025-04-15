# Create main directories
New-Item -ItemType Directory -Force -Path "src"
New-Item -ItemType Directory -Force -Path "src\frontend"
New-Item -ItemType Directory -Force -Path "src\backend"
New-Item -ItemType Directory -Force -Path "src\backend\auth_service"
New-Item -ItemType Directory -Force -Path "src\backend\celery_tasks"
New-Item -ItemType Directory -Force -Path "src\backend\grouping_service"
New-Item -ItemType Directory -Force -Path "src\backend\search_service"
New-Item -ItemType Directory -Force -Path "src\backend\summarization_service"
New-Item -ItemType Directory -Force -Path "src\backend\tagging_service"

# Create other required directories
New-Item -ItemType Directory -Force -Path "research"
New-Item -ItemType Directory -Force -Path "notebooks"
New-Item -ItemType Directory -Force -Path "tests"
New-Item -ItemType Directory -Force -Path "tests\unit"
New-Item -ItemType Directory -Force -Path "tests\integration"
New-Item -ItemType Directory -Force -Path "tests\e2e"
New-Item -ItemType Directory -Force -Path "tests\performance"

# Create config directories
New-Item -ItemType Directory -Force -Path "config\development"
New-Item -ItemType Directory -Force -Path "config\staging"
New-Item -ItemType Directory -Force -Path "config\production"

# Create monitoring directories
New-Item -ItemType Directory -Force -Path "monitoring\dashboards"
New-Item -ItemType Directory -Force -Path "monitoring\alerts"
New-Item -ItemType Directory -Force -Path "monitoring\metrics"

# Create infra directories
New-Item -ItemType Directory -Force -Path "infra\kubernetes"
New-Item -ItemType Directory -Force -Path "infra\terraform"
New-Item -ItemType Directory -Force -Path "infra\scripts"

# Create docs directories
New-Item -ItemType Directory -Force -Path "docs\api"
New-Item -ItemType Directory -Force -Path "docs\architecture"
New-Item -ItemType Directory -Force -Path "docs\deployment"
New-Item -ItemType Directory -Force -Path "docs\development"
New-Item -ItemType Directory -Force -Path "docs\user-guides"

# Move files to their new locations
Move-Item -Path "Summiva_ An Enterprise-Scale NLP System for Content Summarization, Tagging, Grouping, and Search.pdf" -Destination "research\" -Force
Move-Item -Path "Summiva_ An Enterprise-Scale NLP System for Content Summarization, Tagging, Grouping, and Search new.pdf" -Destination "research\" -Force
Move-Item -Path "Summiva_ An Enterprise-Scale NLP System for Content Summarization, Tagging, Grouping, and Search.pdf (150KB, 2023 lines)" -Destination "research\" -Force
Move-Item -Path "notebooks" -Destination "notebooks\" -Force
Move-Item -Path "pubspec.yaml" -Destination "src\frontend\" -Force
Move-Item -Path "Makefile" -Destination "src\backend\" -Force

# Move backend files
if (Test-Path "backend") {
    Move-Item -Path "backend\*" -Destination "src\backend\" -Force
    Remove-Item -Path "backend" -Force
}

# Move frontend files
if (Test-Path "frontend") {
    Move-Item -Path "frontend\*" -Destination "src\frontend\" -Force
    Remove-Item -Path "frontend" -Force
}

# Move models directory
if (Test-Path "models") {
    Move-Item -Path "models\*" -Destination "src\backend\models\" -Force
    Remove-Item -Path "models" -Force
}

# Move logs directory
if (Test-Path "logs") {
    Move-Item -Path "logs\*" -Destination "src\backend\logs\" -Force
    Remove-Item -Path "logs" -Force
}

Write-Host "Project restructuring completed successfully!" 