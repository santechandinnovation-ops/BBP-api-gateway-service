# Deployment Guide - API Gateway su Railway

## Prerequisiti

- Account Railway
- Repository Git con il codice dell'API Gateway
- Gli URL dei tre microservizi già deployati

## Step di Deployment

### 1. Preparazione Repository

Assicurati che il repository contenga:
- `app/` - Directory con il codice dell'applicazione
- `Procfile` - Configurazione per Railway
- `requirements.txt` - Dipendenze Python
- `runtime.txt` - Versione Python

### 2. Creazione Progetto su Railway

1. Vai su [railway.app](https://railway.app)
2. Clicca su "New Project"
3. Seleziona "Deploy from GitHub repo"
4. Autorizza Railway ad accedere al tuo repository
5. Seleziona il repository dell'API Gateway

### 3. Configurazione Variabili d'Ambiente

Nel dashboard di Railway, vai su "Variables" e aggiungi:

```
JWT_SECRET_KEY=<genera-una-chiave-sicura-random>
JWT_ALGORITHM=HS256

USER_SERVICE_URL=https://bbp-path-management-service-production.up.railway.app
TRIP_SERVICE_URL=https://bbp-trip-management-service-production.up.railway.app
PATH_SERVICE_URL=https://web-production-b97f0.up.railway.app

RATE_LIMIT_PER_MINUTE=60
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60
SERVICE_REQUEST_TIMEOUT=30
```

**IMPORTANTE**: Gli URL dei microservizi DEVONO essere configurati. Usa gli URL corretti dei tuoi servizi deployati.

### 4. Deploy

Railway rileverà automaticamente:
- `runtime.txt` per la versione Python
- `requirements.txt` per installare le dipendenze
- `Procfile` per avviare l'applicazione

Il deploy partirà automaticamente.

### 5. Verifica Deploy

Una volta completato il deploy:

1. Railway ti fornirà un URL pubblico (es: `https://your-api-gateway.up.railway.app`)
2. Testa l'health check:
   ```bash
   curl https://your-api-gateway.up.railway.app/health
   ```

3. Dovresti ricevere una risposta tipo:
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

### 6. Test Endpoints

Prova alcuni endpoints:

```bash
# Root
curl https://your-api-gateway.up.railway.app/

# Lista percorsi (pubblico)
curl https://your-api-gateway.up.railway.app/api/paths

# Registrazione utente
curl -X POST https://your-api-gateway.up.railway.app/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'
```

## Monitoraggio

### Logs

Visualizza i log in tempo reale su Railway:
1. Apri il progetto
2. Clicca sulla tab "Deployments"
3. Seleziona il deployment attivo
4. Visualizza i logs

### Metriche

Railway fornisce automaticamente:
- CPU usage
- Memory usage
- Network traffic
- Request count

### Circuit Breaker Status

Monitora lo stato dei circuit breaker via health endpoint:
```bash
curl https://your-api-gateway.up.railway.app/health
```

## Troubleshooting

### Il deploy fallisce

1. Controlla i logs su Railway
2. Verifica che `requirements.txt` sia corretto
3. Verifica che `runtime.txt` specifichi Python 3.11+

### Rate limiting troppo restrittivo

Aumenta il valore di `RATE_LIMIT_PER_MINUTE` nelle variabili d'ambiente

### Circuit breaker si apre troppo spesso

Aumenta `CIRCUIT_BREAKER_FAILURE_THRESHOLD` o `CIRCUIT_BREAKER_TIMEOUT`

### Timeout sulle richieste

Aumenta `SERVICE_REQUEST_TIMEOUT` (default 30 secondi)

## Scaling

Railway permette di scalare automaticamente. Nota:
- Rate limiting è in-memory per istanza
- Circuit breaker è in-memory per istanza
- Per multiple istanze, considera Redis per rate limiting condiviso

## Security Checklist

- [ ] `JWT_SECRET_KEY` configurata con valore sicuro e random
- [ ] CORS configurato appropriatamente per il dominio frontend
- [ ] Rate limiting attivo
- [ ] Circuit breaker configurato
- [ ] HTTPS abilitato (automatico su Railway)

## URL Microservizi

Gli URL dei microservizi sono configurati tramite variabili d'ambiente:
- `USER_SERVICE_URL`: URL del servizio utenti
- `TRIP_SERVICE_URL`: URL del servizio viaggi
- `PATH_SERVICE_URL`: URL del servizio percorsi

Se uno di questi cambia, aggiorna le variabili d'ambiente su Railway (non serve rideploy).
