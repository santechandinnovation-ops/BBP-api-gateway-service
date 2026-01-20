# Circuit Breaker Fix - Railway 404 Issue

## Problema Identificato

Il circuit breaker non si apriva quando un servizio era disabilitato su Railway perché:
1. Railway restituisce `404` con `{"detail":"Not Found"}` quando un servizio è offline/disabilitato
2. Il circuit breaker originale considerava solo errori di connessione/timeout come fallimenti
3. I 404 venivano trattati come risposte legittime (success) invece che come fallimenti del servizio

## Modifiche Implementate

### 1. Logica di Rilevamento Railway Down (`app/services/proxy.py`)

Migliorata la funzione `_is_railway_service_down()` per rilevare quando Railway restituisce errori generici:

**Casi rilevati come "Service Down":**
- 404 con `{"detail": "Not Found"}` (errore generico di Railway)
- 404 con campo `detail` vuoto o mancante
- 404 con `message` contenente frasi come "service not found", "application not found", etc.
- 404 con JSON molto semplice (solo campo `detail` con testo generico)
- 404 con risposta HTML o testo vuoto
- 404 con risposta di testo molto breve (<100 caratteri)

**Casi considerati 404 legittimi da servizi funzionanti:**
- 404 con JSON strutturato e specifico dell'applicazione (es: `{"detail": "User with ID '12345' not found", "error_code": "USER_NOT_FOUND"}`)

### 2. Logging Dettagliato

Aggiunto logging estensivo per debugging:

**In `app/services/proxy.py`:**
- Log di ogni check Railway con dettagli completi
- Log di ogni decisione (successo vs fallimento) del circuit breaker

**In `app/utils/circuit_breaker.py`:**
- Log di ogni fallimento registrato con contatore corrente
- Log quando il circuit si apre (threshold raggiunto)

**In `app/routes/auth_routes.py`:**
- Log di chiamate alle route principali per verifica flusso

### 3. Propagazione Corretta Status Code

Le route ora propagano correttamente lo status code delle risposte:

**File modificati:**
- `app/utils/response_helper.py` - Nuova utility per creare risposte consistenti
- Tutte le route in: `auth_routes.py`, `user_routes.py`, `trip_routes.py`, `path_routes.py`

**Prima:**
```python
return response["content"]  # Restituiva sempre 200
```

**Dopo:**
```python
return create_response_from_proxy(response)  # Restituisce lo status code corretto
```

## Come Testare

### 1. Preparazione

Assicurati che il gateway sia deployato su Railway con le nuove modifiche.

### 2. Test del Circuit Breaker

```bash
#!/bin/bash

BASE_URL="https://bbp-api-gateway-service-production.up.railway.app"

echo "=== TEST CIRCUIT BREAKER ==="

# 1. Verifica stato iniziale
echo "1. Stato iniziale:"
curl -s "$BASE_URL/health" | jq .circuit_breakers

# 2. Disabilita il servizio user su Railway
echo "2. Disabilita il servizio user-management su Railway Dashboard"
read -p "Premi INVIO quando il servizio è disabilitato..."

# 3. Esegui 5 chiamate che falliranno
echo "3. Eseguo 5 chiamate (dovrebbero fallire e incrementare il counter):"
for i in {1..5}; do
  echo "   Tentativo $i/5..."
  curl -s -X POST "$BASE_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"username":"test","email":"test@example.com","password":"Test123!"}' \
    -w "\n   Status: %{http_code}\n"
  sleep 1
done

# 4. Verifica che il circuit sia OPEN
echo "4. Stato dopo 5 fallimenti (dovrebbe essere OPEN):"
curl -s "$BASE_URL/health" | jq .circuit_breakers

# 5. Prova un'altra chiamata (dovrebbe essere bloccata con 503)
echo "5. Prova chiamata con circuit OPEN (dovrebbe restituire 503):"
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"Test123!"}' \
  -w "\nStatus: %{http_code}\n"

# 6. Verifica stato finale
echo "6. Stato finale:"
curl -s "$BASE_URL/health" | jq .circuit_breakers

echo ""
echo "=== TEST COMPLETATO ==="
```

### 3. Verifica dei Log

Controlla i log su Railway Dashboard per vedere l'output dettagliato:

**Cerca questi pattern:**
```
[RAILWAY CHECK] status=404, is_json=True, ...
[RAILWAY CHECK] Found detail field: 'Not Found'
[RAILWAY CHECK] MATCH: detail == 'Not Found' (Railway generic error) -> Service is DOWN
[CIRCUIT BREAKER] Recording FAILURE for user-service
[CIRCUIT BREAKER] user-service - Failure recorded. Count: 1/5
...
[CIRCUIT BREAKER] user-service - Failure recorded. Count: 5/5
[CIRCUIT BREAKER] user-service - OPENING CIRCUIT (threshold reached)
```

### 4. Risultati Attesi

**Dopo 5 chiamate fallite:**
- Circuit breaker stato: `OPEN`
- Chiamate successive: HTTP 503 con messaggio `"user-service service is currently unavailable"`

**Dopo 60 secondi (timeout):**
- Circuit breaker passa automaticamente a: `HALF_OPEN`
- Una chiamata di test viene permessa
- Se fallisce ancora: torna a `OPEN`
- Se ha successo: torna a `CLOSED`

## Configurazione

I parametri del circuit breaker sono in `app/config/settings.py`:

```python
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5  # Numero di fallimenti prima di aprire
CIRCUIT_BREAKER_TIMEOUT = 60  # Secondi prima di provare di nuovo (HALF_OPEN)
```

## Note Importanti

1. **Railway 404 vs 404 Legittimo**: Il sistema ora distingue tra:
   - 404 generico di Railway (servizio down) → Registra FALLIMENTO
   - 404 specifico dell'applicazione (risorsa non trovata) → Registra SUCCESSO

2. **Logging**: I log sono molto dettagliati durante il debugging. Considera di rimuovere o ridurre i log in produzione per performance.

3. **Status Code**: Tutte le route ora propagano correttamente lo status code del servizio backend, migliorando la trasparenza dell'API Gateway.

4. **Test Locali**: Il file `test_circuit_breaker_local.py` può essere usato per testare la logica di rilevamento Railway (richiede dipendenze installate).

## Rollback

Se necessario fare rollback, i file principali modificati sono:
- `app/services/proxy.py`
- `app/utils/circuit_breaker.py`
- `app/utils/response_helper.py` (nuovo)
- `app/routes/*.py` (tutte le route)

Ripristina le versioni precedenti di questi file e rimuovi `response_helper.py`.
