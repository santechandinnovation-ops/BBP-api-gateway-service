from enum import Enum
from datetime import datetime, timedelta
from typing import Dict
from app.config.settings import settings

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self):
        self.circuits: Dict[str, dict] = {}

    def _get_circuit(self, service_name: str) -> dict:
        if service_name not in self.circuits:
            self.circuits[service_name] = {
                "state": CircuitState.CLOSED,
                "failure_count": 0,
                "last_failure_time": None,
                "success_count": 0
            }
        return self.circuits[service_name]

    def can_execute(self, service_name: str) -> bool:
        circuit = self._get_circuit(service_name)

        if circuit["state"] == CircuitState.CLOSED:
            return True

        if circuit["state"] == CircuitState.OPEN:
            if circuit["last_failure_time"]:
                timeout_expired = datetime.now() > circuit["last_failure_time"] + timedelta(
                    seconds=settings.CIRCUIT_BREAKER_TIMEOUT
                )
                if timeout_expired:
                    circuit["state"] = CircuitState.HALF_OPEN
                    circuit["success_count"] = 0
                    return True
            return False

        return True

    def record_success(self, service_name: str):
        circuit = self._get_circuit(service_name)

        if circuit["state"] == CircuitState.HALF_OPEN:
            circuit["success_count"] += 1
            if circuit["success_count"] >= 2:
                circuit["state"] = CircuitState.CLOSED
                circuit["failure_count"] = 0
        else:
            circuit["failure_count"] = 0

    def record_failure(self, service_name: str):
        circuit = self._get_circuit(service_name)
        circuit["failure_count"] += 1
        circuit["last_failure_time"] = datetime.now()

        print(f"[CIRCUIT BREAKER] {service_name} - Failure recorded. Count: {circuit['failure_count']}/{settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD}, State: {circuit['state'].value}")

        if circuit["failure_count"] >= settings.CIRCUIT_BREAKER_FAILURE_THRESHOLD:
            print(f"[CIRCUIT BREAKER] {service_name} - OPENING CIRCUIT (threshold reached)")
            circuit["state"] = CircuitState.OPEN

    def get_state(self, service_name: str) -> CircuitState:
        circuit = self._get_circuit(service_name)
        return circuit["state"]

circuit_breaker = CircuitBreaker()
