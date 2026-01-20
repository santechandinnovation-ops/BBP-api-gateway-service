#!/usr/bin/env python3
"""
Test della logica semplificata del circuit breaker.
Mostra come vengono trattati i vari status code.
"""

def test_circuit_breaker_logic():
    print("=" * 60)
    print("TEST: Logica Semplificata Circuit Breaker")
    print("=" * 60)
    print()

    test_cases = [
        # (status_code, descrizione, azione_attesa)
        (200, "Successo", "SUCCESS ✓ (resetta counter)"),
        (201, "Creato", "SUCCESS ✓ (resetta counter)"),
        (301, "Redirect", "SUCCESS ✓ (resetta counter)"),
        (400, "Bad Request", "IGNORATO ⊘ (non influenza circuit)"),
        (401, "Unauthorized", "IGNORATO ⊘ (non influenza circuit)"),
        (403, "Forbidden", "IGNORATO ⊘ (non influenza circuit)"),
        (404, "Not Found", "FAILURE ✗ (counter +1)"),
        (500, "Internal Server Error", "FAILURE ✗ (counter +1)"),
        (502, "Bad Gateway", "FAILURE ✗ (counter +1)"),
        (503, "Service Unavailable", "FAILURE ✗ (counter +1)"),
    ]

    print(f"{'Status':<10} {'Descrizione':<25} {'Azione'}")
    print("-" * 60)

    for status, desc, action in test_cases:
        print(f"{status:<10} {desc:<25} {action}")

    print()
    print("=" * 60)
    print("RIEPILOGO")
    print("=" * 60)
    print()
    print("✗ FAILURE (conta verso apertura):")
    print("  - 404 (Not Found)")
    print("  - 500+ (Server Errors)")
    print()
    print("✓ SUCCESS (resetta counter):")
    print("  - 200-399 (Success, Redirects)")
    print()
    print("⊘ IGNORATO (non influenza circuit):")
    print("  - 400-403, 405-499 (Client Errors)")
    print()
    print("THRESHOLD: 5 fallimenti consecutivi → Circuit OPEN")
    print("TIMEOUT: 60 secondi → Circuit passa a HALF_OPEN")
    print()

    # Simulazione
    print("=" * 60)
    print("SIMULAZIONE: Servizio disabilitato su Railway")
    print("=" * 60)
    print()

    failure_count = 0
    threshold = 5

    for i in range(1, 6):
        print(f"Richiesta {i}: Status 404 (Railway service down)")
        failure_count += 1
        print(f"  → FAILURE registrato. Counter: {failure_count}/{threshold}")

        if failure_count >= threshold:
            print(f"  → 🔴 CIRCUIT OPEN! (threshold raggiunto)")
            break
        print()

    print()
    print("Richiesta 6: Status 404")
    print("  → ⛔ BLOCCATA! Circuit is OPEN")
    print("  → Risposta: HTTP 503 'user-service is currently unavailable'")
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_circuit_breaker_logic()
