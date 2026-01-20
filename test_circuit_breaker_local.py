#!/usr/bin/env python3
"""
Test script per verificare il circuit breaker localmente.
Questo script simula le risposte di Railway per testare la logica.
"""

from app.services.proxy import ServiceProxy

def test_railway_detection():
    """Test della funzione _is_railway_service_down"""
    proxy = ServiceProxy()

    print("=" * 60)
    print("TEST: Railway Service Down Detection")
    print("=" * 60)

    test_cases = [
        {
            "name": "Railway generic 404",
            "status": 404,
            "content": {"detail": "Not Found"},
            "is_json": True,
            "content_type": "application/json",
            "expected": True
        },
        {
            "name": "Empty 404",
            "status": 404,
            "content": "",
            "is_json": False,
            "content_type": "text/plain",
            "expected": True
        },
        {
            "name": "HTML 404",
            "status": 404,
            "content": "<html><body>Not Found</body></html>",
            "is_json": False,
            "content_type": "text/html",
            "expected": True
        },
        {
            "name": "Application-specific 404 (user not found)",
            "status": 404,
            "content": {
                "detail": "User with ID '12345' not found",
                "error_code": "USER_NOT_FOUND",
                "timestamp": "2024-01-20T10:00:00Z"
            },
            "is_json": True,
            "content_type": "application/json",
            "expected": False
        },
        {
            "name": "Successful response (200)",
            "status": 200,
            "content": {"message": "OK"},
            "is_json": True,
            "content_type": "application/json",
            "expected": False
        },
        {
            "name": "Server error (500)",
            "status": 500,
            "content": {"detail": "Internal Server Error"},
            "is_json": True,
            "content_type": "application/json",
            "expected": False
        }
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        result = proxy._is_railway_service_down(
            test["status"],
            test["content"],
            test["is_json"],
            test["content_type"]
        )

        status = "✓ PASS" if result == test["expected"] else "✗ FAIL"
        if result == test["expected"]:
            passed += 1
        else:
            failed += 1

        print(f"\n{status}: {test['name']}")
        print(f"  Expected: {test['expected']}, Got: {result}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    import sys
    success = test_railway_detection()
    sys.exit(0 if success else 1)
