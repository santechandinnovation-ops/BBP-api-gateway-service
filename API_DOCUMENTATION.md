# API Gateway - Documentazione Endpoints

Base URL: `https://your-api-gateway.up.railway.app`

## Autenticazione

Gli endpoints protetti richiedono un JWT Bearer token nell'header:
```
Authorization: Bearer <your-jwt-token>
```

Il token viene ottenuto tramite login e deve essere incluso in tutte le richieste autenticate.

---

## Health & Info

### GET /
Informazioni base sul gateway

**Response:**
```json
{
  "service": "BBP API Gateway",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "users": "/api/users",
    "trips": "/api/trips",
    "paths": "/api/paths"
  }
}
```

### GET /health
Health check del gateway e stato dei circuit breaker

**Response:**
```json
{
  "status": "healthy",
  "service": "api-gateway",
  "circuit_breakers": {
    "user-service": "closed",
    "trip-service": "closed",
    "path-service": "closed"
  }
}
```

---

## Users API

### POST /api/users/register
Registrazione nuovo utente

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "is_blind": false
}
```

**Response:** `201 Created`
```json
{
  "user_id": "uuid",
  "username": "john_doe",
  "email": "john@example.com"
}
```

### POST /api/users/login
Login utente

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "user_id": "uuid",
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

### GET /api/users/profile
Ottieni profilo utente corrente (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "user_id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "is_blind": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### PUT /api/users/profile
Aggiorna profilo utente (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "username": "john_updated",
  "is_blind": true
}
```

**Response:** `200 OK`

### GET /api/users/{user_id}
Ottieni informazioni pubbliche di un utente

**Response:** `200 OK`
```json
{
  "user_id": "uuid",
  "username": "john_doe",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Trips API

### POST /api/trips
Crea nuovo viaggio (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "user_id": "uuid",
  "path_id": "uuid",
  "start_location": {
    "latitude": 45.4642,
    "longitude": 9.1900
  },
  "end_location": {
    "latitude": 45.4700,
    "longitude": 9.2000
  }
}
```

**Response:** `201 Created`
```json
{
  "trip_id": "uuid",
  "user_id": "uuid",
  "path_id": "uuid",
  "status": "planned",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/trips
Lista tutti i viaggi (con filtri opzionali)

**Query Parameters:**
- `status`: Filter by status (planned, in_progress, completed)
- `user_id`: Filter by user
- `limit`: Number of results (default 50)
- `offset`: Pagination offset

**Response:** `200 OK`
```json
{
  "trips": [
    {
      "trip_id": "uuid",
      "user_id": "uuid",
      "status": "completed",
      "start_time": "2024-01-01T10:00:00Z",
      "end_time": "2024-01-01T10:30:00Z"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### GET /api/trips/{trip_id}
Dettagli di un viaggio specifico

**Response:** `200 OK`
```json
{
  "trip_id": "uuid",
  "user_id": "uuid",
  "path_id": "uuid",
  "status": "completed",
  "start_location": {"latitude": 45.4642, "longitude": 9.1900},
  "end_location": {"latitude": 45.4700, "longitude": 9.2000},
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T10:30:00Z",
  "distance_km": 2.5
}
```

### PUT /api/trips/{trip_id}
Aggiorna viaggio (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "status": "in_progress"
}
```

**Response:** `200 OK`

### DELETE /api/trips/{trip_id}
Elimina viaggio (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `204 No Content`

### POST /api/trips/{trip_id}/start
Inizia un viaggio (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "start_time": "2024-01-01T10:00:00Z"
}
```

**Response:** `200 OK`

### POST /api/trips/{trip_id}/complete
Completa un viaggio (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "end_time": "2024-01-01T10:30:00Z",
  "actual_path": [
    {"latitude": 45.4642, "longitude": 9.1900, "timestamp": "2024-01-01T10:00:00Z"},
    {"latitude": 45.4650, "longitude": 9.1920, "timestamp": "2024-01-01T10:10:00Z"}
  ]
}
```

**Response:** `200 OK`

### GET /api/trips/user/{user_id}
Ottieni viaggi di un utente specifico (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`

---

## Paths API

### POST /api/paths
Crea nuovo percorso (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "user_id": "uuid",
  "name": "Via Dante - Via Verdi",
  "start_location": {
    "latitude": 45.4642,
    "longitude": 9.1900
  },
  "end_location": {
    "latitude": 45.4700,
    "longitude": 9.2000
  },
  "waypoints": [
    {"latitude": 45.4650, "longitude": 9.1920, "order": 1},
    {"latitude": 45.4670, "longitude": 9.1950, "order": 2}
  ],
  "accessibility_score": 8.5,
  "is_verified": false
}
```

**Response:** `201 Created`
```json
{
  "path_id": "uuid",
  "name": "Via Dante - Via Verdi",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### GET /api/paths
Lista tutti i percorsi (con filtri)

**Query Parameters:**
- `min_accessibility`: Minimum accessibility score
- `is_verified`: Filter by verification status
- `limit`: Number of results
- `offset`: Pagination offset

**Response:** `200 OK`
```json
{
  "paths": [
    {
      "path_id": "uuid",
      "name": "Via Dante - Via Verdi",
      "accessibility_score": 8.5,
      "distance_km": 2.3,
      "is_verified": true
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

### GET /api/paths/search
Cerca percorsi per coordinate

**Query Parameters:**
- `start_lat`: Starting latitude
- `start_lon`: Starting longitude
- `end_lat`: Ending latitude
- `end_lon`: Ending longitude
- `max_distance`: Maximum distance in km
- `min_accessibility`: Minimum accessibility score

**Response:** `200 OK`
```json
{
  "paths": [
    {
      "path_id": "uuid",
      "name": "Via Dante - Via Verdi",
      "distance_from_query": 0.5,
      "accessibility_score": 8.5
    }
  ]
}
```

### GET /api/paths/{path_id}
Dettagli percorso specifico

**Response:** `200 OK`
```json
{
  "path_id": "uuid",
  "user_id": "uuid",
  "name": "Via Dante - Via Verdi",
  "start_location": {"latitude": 45.4642, "longitude": 9.1900},
  "end_location": {"latitude": 45.4700, "longitude": 9.2000},
  "waypoints": [...],
  "obstacles": [...],
  "accessibility_score": 8.5,
  "distance_km": 2.3,
  "is_verified": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### PUT /api/paths/{path_id}
Aggiorna percorso (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Updated Path Name",
  "accessibility_score": 9.0
}
```

**Response:** `200 OK`

### DELETE /api/paths/{path_id}
Elimina percorso (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `204 No Content`

### POST /api/paths/{path_id}/obstacles
Aggiungi ostacolo a percorso (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "location": {
    "latitude": 45.4660,
    "longitude": 9.1930
  },
  "type": "stairs",
  "severity": "high",
  "description": "3 gradini senza rampa"
}
```

**Response:** `201 Created`

### GET /api/paths/{path_id}/obstacles
Lista ostacoli di un percorso

**Response:** `200 OK`
```json
{
  "obstacles": [
    {
      "obstacle_id": "uuid",
      "type": "stairs",
      "severity": "high",
      "location": {"latitude": 45.4660, "longitude": 9.1930},
      "description": "3 gradini senza rampa",
      "reported_by": "uuid",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### GET /api/paths/user/{user_id}
Percorsi creati da un utente (richiede auth)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`

---

## Rate Limiting

- Default: 60 richieste per minuto per IP
- Header di risposta quando rate limit attivo:
  - `X-RateLimit-Limit`: Limite totale
  - `X-RateLimit-Remaining`: Richieste rimanenti
  - `X-RateLimit-Reset`: Timestamp reset

**Response quando rate limit superato:** `429 Too Many Requests`
```json
{
  "error": "Rate limit exceeded"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

### 502 Bad Gateway
```json
{
  "detail": "user-service service unavailable"
}
```

### 503 Service Unavailable
```json
{
  "detail": "trip-service service is currently unavailable"
}
```

### 504 Gateway Timeout
```json
{
  "detail": "path-service service timeout"
}
```
