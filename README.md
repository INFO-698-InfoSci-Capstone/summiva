![Summiva Logo](assets/summiva-logo.png)

## Overview

Summiva is an enterprise-scale NLP system designed for content summarization, tagging, grouping, and search.

## Prerequisites

-   Docker
-   Docker Compose

## Development Setup

1.  Copy the `.env.example` file to a new file called `.env`:
```
bash
    cp .env.example .env
    
```
2.  Modify the `.env` file to set your desired environment variables.

## Running the services

To start the project in development mode, run:
```
bash
    docker compose up
    
```
## Running Tests

To run the tests, execute the following command:
```
bash
    docker compose run backend pytest
    
```
## Deployment

To deploy the application, use the following command: