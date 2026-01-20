# API Gateway Route Mapping

This document maps the Gateway routes to the corresponding Microservice routes.

## Architecture Overview

- **Gateway Base URL**: `http://gateway:8080`
- **API Prefix**: `/api`
- **All API routes**: `/api/{service}/{endpoint}`

## Authentication Routes (`/api/auth`)

| Gateway Route | Method | Microservice Route | Service | Auth Required |
|--------------|--------|-------------------|---------|---------------|
| `/api/auth/register` | POST | `/auth/register` | User Service | No |
| `/api/auth/login` | POST | `/auth/login` | User Service | No |
| `/api/auth/logout` | POST | `/auth/logout` | User Service | Yes |

## User Routes (`/api/users`)

| Gateway Route | Method | Microservice Route | Service | Auth Required |
|--------------|--------|-------------------|---------|---------------|
| `/api/users/profile` | GET | `/users/profile` | User Service | Yes |
| `/api/users/profile` | PUT | `/users/profile` | User Service | Yes |
| `/api/users/{user_id}` | GET | `/users/{user_id}` | User Service | Optional |

## Path Routes (`/api/paths`)

| Gateway Route | Method | Microservice Route | Service | Auth Required |
|--------------|--------|-------------------|---------|---------------|
| `/api/paths/manual` | POST | `/paths/manual` | Path Service | Yes |
| `/api/paths` | GET | `/paths` | Path Service | Optional |
| `/api/paths/search` | GET | `/paths/search` | Path Service | Optional |
| `/api/paths/{path_id}` | GET | `/paths/{path_id}` | Path Service | Optional |
| `/api/paths/{path_id}` | PUT | `/paths/{path_id}` | Path Service | Yes |
| `/api/paths/{path_id}` | DELETE | `/paths/{path_id}` | Path Service | Yes |
| `/api/paths/{path_id}/obstacles` | POST | `/paths/{path_id}/obstacles` | Path Service | Yes |
| `/api/paths/{path_id}/obstacles` | GET | `/paths/{path_id}/obstacles` | Path Service | Optional |
| `/api/paths/user/{user_id}` | GET | `/paths/user/{user_id}` | Path Service | Yes |

### Path Service Note
The Path Service exposes the same routes under both `/paths` and `/routes` prefixes.
- Routes are accessible via: `/paths/*` and `/routes/*`
- Gateway only uses `/paths/*` for consistency

## Trip Routes (`/api/trips`)

| Gateway Route | Method | Microservice Route | Service | Auth Required |
|--------------|--------|-------------------|---------|---------------|
| `/api/trips` | POST | `/trips` | Trip Service | Yes |
| `/api/trips` | GET | `/trips` | Trip Service | Optional |
| `/api/trips/{trip_id}` | GET | `/trips/{trip_id}` | Trip Service | Optional |
| `/api/trips/{trip_id}` | PUT | `/trips/{trip_id}` | Trip Service | Yes |
| `/api/trips/{trip_id}` | DELETE | `/trips/{trip_id}` | Trip Service | Yes |
| `/api/trips/{trip_id}/coordinates` | POST | `/trips/{trip_id}/coordinates` | Trip Service | Yes |
| `/api/trips/{trip_id}/complete` | PUT | `/trips/{trip_id}/complete` | Trip Service | Yes |
| `/api/trips/user/{user_id}` | GET | `/trips/user/{user_id}` | Trip Service | Yes |

## Health Check

| Gateway Route | Method | Description |
|--------------|--------|-------------|
| `/health` | GET | Gateway health check |
| `/` | GET | Gateway service info |

## Service URLs (Environment Variables)

The gateway forwards requests to these services:

- `USER_SERVICE_URL` - User Management Service
- `PATH_SERVICE_URL` - Path Management Service
- `TRIP_SERVICE_URL` - Trip Management Service

## Rate Limiting

All routes are rate-limited to 60 requests per minute per IP address (configurable via `RATE_LIMIT_PER_MINUTE`).

## Authentication

- **Required**: Route requires valid JWT token in Authorization header
- **Optional**: Route accepts both authenticated and anonymous requests
- **No**: Public route, no authentication needed

JWT tokens are obtained via `/api/auth/login` and should be sent as:
```
Authorization: Bearer <token>
```
