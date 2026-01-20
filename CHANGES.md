# Modifiche Apportate all'API Gateway

## Riepilogo

L'API Gateway è stato ristrutturato per correggere i problemi di routing e standardizzare l'architettura delle API. Tutte le rotte ora utilizzano il prefisso `/api` e i path vengono correttamente inoltrati ai microservizi.

## Modifiche Principali

### 1. Aggiunto Prefisso `/api` Globale

**File modificato**: `app/main.py`

Tutti i router ora sono registrati con il prefisso `/api`:
- `/auth` → `/api/auth`
- `/users` → `/api/users`
- `/trips` → `/api/trips`
- `/paths` → `/api/paths`

La rotta `/health` rimane senza prefisso per compatibilità con i sistemi di monitoraggio.

### 2. Corretti Path Service Routes

**File modificato**: `app/routes/path_routes.py`

Tutti i path inoltrati al Path Service ora includono il prefisso `/paths`:
- `path="/"` → `path="/paths"`
- `path="/search"` → `path="/paths/search"`
- `path=f"/{path_id}"` → `path=f"/paths/{path_id}"`
- E così via per tutte le altre rotte

**Nuova rotta aggiunta**:
- `POST /api/paths/manual` per creare percorsi manuali

### 3. Corretti Trip Service Routes

**File modificato**: `app/routes/trip_routes.py`

**Modifiche**:
- Rimossa rotta `POST /{trip_id}/start` (non esistente nel servizio)
- Aggiunta rotta `POST /{trip_id}/coordinates` per aggiungere coordinate GPS
- Corretto metodo `POST` → `PUT` per `/{trip_id}/complete`

### 4. Aggiunto Rate Limiting

**Files modificati**:
- `app/routes/auth_routes.py`
- `app/routes/user_routes.py`
- `app/routes/trip_routes.py`

Tutte le rotte ora hanno rate limiting configurato (60 req/min per IP).

### 5. Variabili d'Ambiente

**File modificato**: `.env`

Aggiunte le variabili necessarie per i microservizi:
```
USER_SERVICE_URL=http://localhost:8000
PATH_SERVICE_URL=http://localhost:8001
TRIP_SERVICE_URL=http://localhost:8002
```

### 6. Test Aggiornati

**File modificato**: `test_gateway.py`

- Corretto endpoint registrazione: `/api/users/register` → `/api/auth/register`
- Aggiornata funzione test per paths: ora testa `/api/paths/search` con parametri corretti

### 7. Documentazione

**Nuovi files creati**:
- `ROUTE_MAPPING.md` - Mappatura completa delle rotte gateway → microservizi
- `IMPLEMENTATION_STATUS.md` - Stato implementazione delle rotte
- `CHANGES.md` - Questo documento

**File aggiornato**:
- `README.md` - Documentazione completa aggiornata con nuove rotte

## Struttura Finale delle Rotte

### Gateway → User Service
```
/api/auth/register  → /auth/register
/api/auth/login     → /auth/login
/api/auth/logout    → /auth/logout
/api/users/profile  → /users/profile
/api/users/{id}     → /users/{id}
```

### Gateway → Path Service
```
/api/paths/manual         → /paths/manual
/api/paths               → /paths
/api/paths/search        → /paths/search
/api/paths/{id}          → /paths/{id}
/api/paths/{id}/obstacles → /paths/{id}/obstacles
```

### Gateway → Trip Service
```
/api/trips                    → /trips
/api/trips/{id}              → /trips/{id}
/api/trips/{id}/coordinates  → /trips/{id}/coordinates
/api/trips/{id}/complete     → /trips/{id}/complete
```

## Compatibilità

### Breaking Changes
- Tutte le rotte ora richiedono il prefisso `/api`
- I client devono aggiornare gli URL da `/auth/login` a `/api/auth/login`, ecc.
- Il metodo per completare un trip è cambiato da `POST` a `PUT`

### Non Breaking
- La rotta `/health` rimane invariata
- Le intestazioni di autenticazione rimangono le stesse

## Test

Per testare le modifiche:

1. Avvia i microservizi sulle porte 8000, 8001, 8002
2. Avvia il gateway: `uvicorn app.main:app --reload --port 8080`
3. Esegui i test: `python test_gateway.py`
4. Verifica gli endpoint con: `curl http://localhost:8080/`

## Prossimi Passi

1. Implementare le rotte mancanti nei microservizi (vedi `IMPLEMENTATION_STATUS.md`)
2. Aggiornare eventuali client/frontend per usare il prefisso `/api`
3. Configurare CORS in modo più restrittivo per production
4. Considerare Redis per rate limiting in ambienti multi-istanza
5. Aggiungere logging strutturato e metriche

## Note Importanti

- Alcune rotte sono esposte nel gateway ma non ancora implementate nei microservizi
- Il Path Service espone le stesse rotte sotto `/paths` e `/routes` (il gateway usa solo `/paths`)
- Rate limiting è in-memory e si resetta al riavvio
- Circuit breaker monitora la salute dei servizi e apre il circuito dopo 5 fallimenti consecutivi
