# Summiva API Documentation

## Overview
This document describes the REST APIs provided by Summiva's microservices architecture.

## Base URLs
- Development: `http://localhost:8000`
- Staging: `https://api-staging.summiva.com`
- Production: `https://api.summiva.com`

## Authentication Service
Base path: `/auth`

### Login
```http
POST /auth/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

Response:
```json
{
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 3600
}
```

### Register
```http
POST /auth/register
Content-Type: application/json

{
    "username": "string",
    "email": "string",
    "password": "string"
}
```

## Summarization Service
Base path: `/summarize`

### Create Summary
```http
POST /summarize
Content-Type: application/json
Authorization: Bearer <token>

{
    "text": "string",
    "max_length": integer,
    "min_length": integer,
    "type": "extractive|abstractive"
}
```

## Tagging Service
Base path: `/tag`

### Tag Content
```http
POST /tag
Content-Type: application/json
Authorization: Bearer <token>

{
    "text": "string",
    "max_tags": integer
}
```

## Search Service
Base path: `/search`

### Search Content
```http
GET /search?q=query&page=1&size=10
Authorization: Bearer <token>
```

## Grouping Service
Base path: `/group`

### Group Content
```http
POST /group
Content-Type: application/json
Authorization: Bearer <token>

{
    "texts": ["string"],
    "algorithm": "bertopic|lda|hdbscan"
}
```

## Error Codes
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

## Rate Limiting
All APIs are rate-limited to:
- 100 requests per minute for free tier
- 1000 requests per minute for premium tier

## Versioning
The API version is included in the URL path:
- v1: `/api/v1/`
- v2: `/api/v2/` 