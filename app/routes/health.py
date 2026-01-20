from fastapi import APIRouter
from app.utils.circuit_breaker import circuit_breaker

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "api-gateway",
        "circuit_breakers": {
            "user-service": circuit_breaker.get_state("user-service").value,
            "trip-service": circuit_breaker.get_state("trip-service").value,
            "path-service": circuit_breaker.get_state("path-service").value
        }
    }
