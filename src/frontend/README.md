# Summiva - NicegUI Frontend

This directory contains the NicegUI-based frontend for the Summiva NLP summarization system.

## Features

- User authentication and authorization
- URL summarization using the Summiva backend services
- Tagging and grouping of content
- Advanced search functionality
- Responsive UI with dark mode support

## Architecture

The frontend integrates with the Summiva microservice architecture through REST API calls:

- Auth service for user authentication
- Summarization service for generating summaries from URLs
- Tagging service for extracting relevant tags
- Grouping service for categorizing content
- Search service for content discovery

## Development

### Local Development

To run the frontend locally:

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```
   export BACKEND_BASE_URL=http://localhost:8000  # Adjust as needed
   ```

3. Run the development server:
   ```
   python app.py
   ```

4. Access the UI at http://localhost:8080

### Docker Development

To run the frontend with Docker:

```bash
docker build -t summiva-frontend .
docker run -p 8080:8080 -e BACKEND_BASE_URL=http://localhost:8000 summiva-frontend
```

## Integration with Summiva

The frontend integrates with all Summiva microservices:

- Uses JWT tokens for authentication
- Communicates with backend services via RESTful APIs
- Handles both authenticated and guest user modes
- Falls back to offline mode when backend services are unavailable

## Environment Variables

- `PORT`: Port to run the frontend server (default: 8080)
- `BACKEND_BASE_URL`: Base URL for backend services
- `AUTH_SERVICE_URL`: URL for the auth service
- `SUMMARIZATION_SERVICE_URL`: URL for the summarization service
- `TAGGING_SERVICE_URL`: URL for the tagging service
- `GROUPING_SERVICE_URL`: URL for the grouping service
- `SEARCH_SERVICE_URL`: URL for the search service

## Future Improvements

- Real-time updates using WebSockets
- PDF and document upload support
- Enhanced visualization of summary data
- User preferences and settings