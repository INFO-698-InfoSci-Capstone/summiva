FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default environment variables
ENV PORT=8080
ENV BACKEND_BASE_URL=http://backend:8000

EXPOSE 8080

# Run the app with host 0.0.0.0 to make it accessible outside the container
CMD ["python", "app.py"]