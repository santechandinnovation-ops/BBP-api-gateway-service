# BBP API Gateway

API Gateway stateless per il sistema BBP (Bike-friendly Blind Paths). Fornisce un punto di accesso unificato per tutti i microservizi del sistema.

## Caratteristiche

- **Stateless**: Nessun database, tutto in-memory
- **Rate Limiting**: Protezione contro abusi (in-memory)
- **Circuit Breaker**: Gestione fallimenti dei microservizi
- **JWT Authentication**: Autenticazione centralizzata
- **Request Proxying**: Inoltro intelligente delle richieste ai microservizi

## Microservizi Backend

Il gateway inoltra le richieste ai seguenti microservizi:

- **User Service**: Gestione utenti e autenticazione (porta 8000)
- **Path Service**: Gestione percorsi e ricerca (porta 8001)
- **Trip Service**: Gestione viaggi e registrazione GPS (porta 8002)

## Endpoints

### Health Check
- `GET /health` - Stato del gateway e dei circuit breakers
- `GET /` - Informazioni servizio e endpoint disponibili

### Authentication (`/api/auth`)
- `POST /api/auth/register` - Registrazione utente
- `POST /api/auth/login` - Login utente
- `POST /api/auth/logout` - Logout utente (auth required)

### Users (`/api/users`)
- `GET /api/users/profile` - Profilo utente autenticato (auth required)
- `PUT /api/users/profile` - Aggiorna profilo (auth required)
- `GET /api/users/{user_id}` - Dettagli utente (auth optional)

### Trips (`/api/trips`)
- `POST /api/trips` - Crea nuovo viaggio (auth required)
- `GET /api/trips` - Storico viaggi (auth optional)
- `GET /api/trips/{trip_id}` - Dettagli viaggio (auth optional)
- `PUT /api/trips/{trip_id}` - Aggiorna viaggio (auth required)
- `DELETE /api/trips/{trip_id}` - Elimina viaggio (auth required)
- `POST /api/trips/{trip_id}/coordinates` - Aggiungi coordinata GPS (auth required)
- `PUT /api/trips/{trip_id}/complete` - Completa viaggio (auth required)
- `GET /api/trips/user/{user_id}` - Viaggi utente (auth required)

### Paths (`/api/paths`)
- `POST /api/paths/manual` - Crea percorso manuale (auth required)
- `GET /api/paths` - Lista percorsi
- `GET /api/paths/search` - Cerca percorsi per origine/destinazione
- `GET /api/paths/{path_id}` - Dettagli percorso
- `PUT /api/paths/{path_id}` - Aggiorna percorso (auth required)
- `DELETE /api/paths/{path_id}` - Elimina percorso (auth required)
- `POST /api/paths/{path_id}/obstacles` - Aggiungi ostacolo (auth required)
- `GET /api/paths/{path_id}/obstacles` - Lista ostacoli
- `GET /api/paths/user/{user_id}` - Percorsi utente (auth required)

**Nota**: Alcune rotte sono esposte nel gateway ma non ancora implementate nei microservizi. Consultare `IMPLEMENTATION_STATUS.md` per i dettagli.

## Configurazione

Le seguenti variabili d'ambiente possono essere configurate:

**Obbligatorie:**
- `USER_SERVICE_URL`: URL del microservizio utenti (richiesto)
- `TRIP_SERVICE_URL`: URL del microservizio viaggi (richiesto)
- `PATH_SERVICE_URL`: URL del microservizio percorsi (richiesto)

**Opzionali:**
- `JWT_SECRET_KEY`: Chiave segreta per JWT (default: your-secret-key-change-in-production)
- `JWT_ALGORITHM`: Algoritmo JWT (default: HS256)
- `RATE_LIMIT_PER_MINUTE`: Rate limit per IP (default: 60)
- `CIRCUIT_BREAKER_FAILURE_THRESHOLD`: Soglia fallimenti per circuit breaker (default: 5)
- `CIRCUIT_BREAKER_TIMEOUT`: Timeout circuit breaker in secondi (default: 60)
- `SERVICE_REQUEST_TIMEOUT`: Timeout richieste ai servizi in secondi (default: 30)

## Deploy su Railway

1. Push del codice su repository Git
2. Crea nuovo progetto su Railway
3. Collega repository
4. Railway rileva automaticamente il Procfile
5. Configura le variabili d'ambiente obbligatorie:
   - `USER_SERVICE_URL`
   - `TRIP_SERVICE_URL`
   - `PATH_SERVICE_URL`
   - `JWT_SECRET_KEY` (genera un valore sicuro per production)

## Sviluppo Locale

### Prerequisiti

Assicurati che i microservizi siano in esecuzione:
- User Service su `http://localhost:8000`
- Path Service su `http://localhost:8001`
- Trip Service su `http://localhost:8002`

### Setup

```bash
# Installa dipendenze
pip install -r requirements.txt

# Configura variabili d'ambiente nel file .env
# (già configurato per sviluppo locale)

# Avvia API Gateway
uvicorn app.main:app --reload --port 8080
```

Il gateway sarà disponibile su `http://localhost:8080`

### Testing

```bash
# Test del gateway
python test_gateway.py
```

Consulta `ROUTE_MAPPING.md` per la mappatura completa delle rotte.

## Rate Limiting

- Default: 60 richieste per minuto per IP
- In-memory storage (si resetta al riavvio)
- Per production con più istanze, considerare Redis

## Circuit Breaker

- Monitora salute dei microservizi
- Dopo 5 fallimenti consecutivi, apre il circuito
- Timeout di 60 secondi prima di tentare recovery
- Half-open state per test graduale

## Sicurezza

- JWT Bearer token per autenticazione
- Rate limiting per prevenire abusi
- CORS configurato per tutti i domini (configurare per production)
- Timeout su tutte le richieste ai microservizi
