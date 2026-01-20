# Test Rapido Circuit Breaker

## Setup Veloce

1. **Deploy su Railway**
   - Le modifiche sono nel codice
   - Fai commit e push su GitHub (se hai auto-deploy)
   - Oppure triggera manualmente il deploy

2. **Aspetta che il deploy sia completo** (~2-5 minuti)

3. **Verifica che il nuovo codice sia attivo**
   ```bash
   # Fai una chiamata qualsiasi e controlla i log su Railway
   curl -X POST https://bbp-api-gateway-service-production.up.railway.app/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"test","email":"test@test.com","password":"Test123!"}'
   ```

   Vai su Railway → Gateway Service → Logs e cerca:
   ```
   [CIRCUIT BREAKER DEBUG] Service: user-service, Status: ...
   [CIRCUIT BREAKER] Recording ...
   ```

   Se vedi questi log, il nuovo codice è attivo! ✓

## Test del Circuit Breaker

### Passo 1: Disabilita il Servizio User

1. Vai su Railway Dashboard
2. Trova `bbp-user-management-service`
3. Click sui 3 puntini → Settings → **Pause Service**
4. Aspetta 30 secondi

### Passo 2: Stato Iniziale

```bash
curl -s https://bbp-api-gateway-service-production.up.railway.app/health | jq .circuit_breakers
```

**Risultato atteso:**
```json
{
  "user-service": "closed",
  "trip-service": "closed",
  "path-service": "closed"
}
```

### Passo 3: Genera 5 Fallimenti

```bash
# Esegui questo comando 5 volte (o usa il loop)
for i in {1..5}; do
  echo "Richiesta $i/5..."
  curl -s -X POST https://bbp-api-gateway-service-production.up.railway.app/auth/register \
    -H "Content-Type: application/json" \
    -d '{"username":"test","email":"test@test.com","password":"Test123!"}' \
    -w "\nHTTP: %{http_code}\n\n"
  sleep 1
done
```

**Risultato atteso:**
- Tutte le richieste: `HTTP 404` con `{"detail":"Not Found"}`

### Passo 4: Verifica Circuit OPEN

```bash
curl -s https://bbp-api-gateway-service-production.up.railway.app/health | jq .circuit_breakers
```

**Risultato atteso:**
```json
{
  "user-service": "open",  ← ✓ OPEN!
  "trip-service": "closed",
  "path-service": "closed"
}
```

### Passo 5: Verifica Blocco

```bash
curl -s -X POST https://bbp-api-gateway-service-production.up.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"Test123!"}' \
  -w "\nHTTP: %{http_code}\n"
```

**Risultato atteso:**
```
HTTP 503
{"detail":"user-service service is currently unavailable"}
```

✅ **TEST SUPERATO!** Il circuit breaker funziona!

## Cosa Cercare nei Log

Su Railway → Gateway Service → Logs, dovresti vedere:

```
[CIRCUIT BREAKER DEBUG] Service: user-service, Status: 404
[CIRCUIT BREAKER] Recording FAILURE for user-service (status=404)
[CIRCUIT BREAKER] user-service - Failure recorded. Count: 1/5, State: closed
[CIRCUIT BREAKER DEBUG] Service: user-service, Status: 404
[CIRCUIT BREAKER] Recording FAILURE for user-service (status=404)
[CIRCUIT BREAKER] user-service - Failure recorded. Count: 2/5, State: closed
...
[CIRCUIT BREAKER] user-service - Failure recorded. Count: 5/5, State: closed
[CIRCUIT BREAKER] user-service - OPENING CIRCUIT (threshold reached)
```

## Ripristino

Dopo il test, riattiva il servizio:

1. Railway Dashboard → `bbp-user-management-service`
2. Click → **Resume Service**
3. Aspetta 60 secondi che il circuit passi a HALF_OPEN
4. Fai una chiamata di test → Circuit torna CLOSED

## Troubleshooting

### Circuit rimane "closed"
- Verifica che il nuovo codice sia deployato (controlla i log)
- Controlla che il servizio user sia effettivamente disabilitato su Railway

### Non vedi i log
- Railway potrebbe avere ritardo nei log (aspetta 10-20 secondi)
- Assicurati di guardare i log del **gateway**, non dello user service

### Test funziona localmente ma non su Railway
- Verifica che tutte le modifiche siano state pushate su GitHub
- Triggera manualmente un re-deploy su Railway
