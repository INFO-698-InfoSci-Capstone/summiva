# Use official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file first
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy the entire application source code
COPY . /app

# Set PYTHONPATH to include src for module imports
ENV PYTHONPATH="/app/src"

# Expose the application port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]