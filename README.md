# BBP API Gateway Service

Central API Gateway for the Best Bike Paths (BBP) microservices architecture.

## Overview

This service acts as a single entry point for all client requests, routing them to the appropriate backend microservices. It handles authentication validation, rate limiting, and circuit breaker patterns for resilience.

## Features

- **Request Routing**: Proxies requests to User, Path, and Trip services
- **Rate Limiting**: 60 requests/minute per client (configurable)
- **Circuit Breaker**: Prevents cascade failures when services are down
- **JWT Validation**: Validates authentication tokens before forwarding requests
- **CORS Support**: Configured for frontend access

## Tech Stack

- FastAPI
- HTTPX (async HTTP client)
- SlowAPI (rate limiting)
- Python-Jose (JWT handling)

## API Endpoints

| Method | Endpoint                | Description         |
|--------|-------------------------|---------------------|
| GET    | `/health`               | Health check        |
| POST   | `/api/auth/register`    | User registration   |
| POST   | `/api/auth/login`       | User login          |
| POST   | `/api/auth/logout`      | User logout         |
| GET    | `/api/users/profile`    | Get user profile    |
| GET    | `/api/paths/search`     | Search bike paths   |
| POST   | `/api/paths/manual`     | Create manual path  |
| POST   | `/api/trips`            | Create new trip     |
| GET    | `/api/trips`            | List user trips     |


## Environment Variables

```
USER_SERVICE_URL=<user-service-url>
PATH_SERVICE_URL=<path-service-url>
TRIP_SERVICE_URL=<trip-service-url>
JWT_SECRET_KEY=<secret-key>
RATE_LIMIT_PER_MINUTE=60
```

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Deployment

Deployed on Railway. See `Procfile` for startup command.
