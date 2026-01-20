# Modifiche Apportate all'API Gateway

## Circuit Breaker Fix - 20 Gennaio 2024 ⚡

### Problema Risolto
Il circuit breaker non si apriva quando Railway restituiva 404 per servizi disabilitati/offline.

### Soluzione: Logica Semplificata
Ogni **404 = FALLIMENTO** (nessuna distinzione tra Railway 404 e 404 applicativi)

**Regole:**
- `404` → FALLIMENTO (conta verso apertura)
- `500+` → FALLIMENTO (conta verso apertura)
- `200-399` → SUCCESSO (resetta counter)
- Altri `4xx` → IGNORATO (non influenza circuit)

**Comportamento:**
1. Servizio offline su Railway → 404
2. Dopo 5x 404 consecutivi → Circuit **OPEN** 🔴
3. Richieste successive → **503** (bloccate)
4. Dopo 60s → Circuit **HALF_OPEN** 🟡 (prova 1 richiesta)
5. Se OK → Circuit **CLOSED** 🟢, altrimenti torna **OPEN** 🔴

**File modificati:**
- `app/services/proxy.py` - Logica semplificata
- `app/utils/circuit_breaker.py` - Logging fallimenti
- `app/routes/*.py` - Propagazione status code
- `app/utils/response_helper.py` - Nuovo helper (creato)

---

## Riepilogo (Modifiche Precedenti)

L'API Gateway è stato corretto per esporre SOLO le rotte effettivamente implementate nei microservizi. Rimosse tutte le rotte fantasma che causavano errori 404.

## Modifiche Principali (Fix Finale)

### 1. Rimossi Trailing Slashes dagli URL

**File modificato**: `.env`

Gli URL dei servizi non devono avere trailing slash:
```
❌ https://example.com/
✅ https://example.com
```

### 2. Rimossa Rotta `GET /api/paths`

**File modificato**: `app/routes/path_routes.py`

Il Path Service NON implementa `GET /paths` (lista tutti i percorsi), quindi rimossa dal gateway.

### 3. Rimosse Rotte Trip Non Implementate

**File modificato**: `app/routes/trip_routes.py`

Rimosse:
- `PUT /api/trips/{trip_id}` (aggiornamento trip)
- `DELETE /api/trips/{trip_id}` (cancellazione trip)
- `GET /api/trips/user/{user_id}` (trips per utente - già coperto da GET /trips con auth)

### 4. Rimossa Rotta `PUT /api/paths/{path_id}`

Il Path Service non implementa update path, rimossa dal gateway.

### 5. Rimossa Rotta `DELETE /api/paths/{path_id}`

Il Path Service non implementa delete path, rimossa dal gateway.

### 6. Rimosse Rotte Obstacles

Il Path Service non ha endpoint dedicati per obstacles (sono gestiti durante la creazione manuale del path).

---

## Storia Modifiche Precedenti

### 1. Aggiunto Prefisso `/api` Globale (MANTENUTO)

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

## Struttura Finale delle Rotte (SOLO IMPLEMENTATE)

### Gateway → User Service ✅
```
POST /api/auth/register  → /auth/register
POST /api/auth/login     → /auth/login
POST /api/auth/logout    → /auth/logout
GET  /api/users/profile  → /users/profile
PUT  /api/users/profile  → /users/profile
GET  /api/users/{id}     → /users/{id}
```

### Gateway → Path Service ✅
```
POST /api/paths/manual   → /paths/manual
GET  /api/paths/search   → /paths/search
GET  /api/paths/{id}     → /paths/{id}
```

### Gateway → Trip Service ✅
```
POST /api/trips                   → /trips
GET  /api/trips                   → /trips
GET  /api/trips/{id}              → /trips/{id}
POST /api/trips/{id}/coordinates  → /trips/{id}/coordinates
PUT  /api/trips/{id}/complete     → /trips/{id}/complete
```

## Compatibilità

### Breaking Changes (da versione precedente)
- Rimosse rotte non implementate:
  - `GET /api/paths` (lista paths)
  - `PUT /api/paths/{id}` (update path)
  - `DELETE /api/paths/{id}` (delete path)
  - `PUT /api/trips/{id}` (update trip)
  - `DELETE /api/trips/{id}` (delete trip)
  - Tutte le rotte obstacles

### Rotte Stabili
- Tutte le rotte documentate corrispondono 1:1 con quelle implementate nei microservizi
- Prefisso `/api` funziona correttamente
- `/health` invariato

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
