from fastapi import APIRouter, Request, Depends
from typing import Optional
from app.services.proxy import proxy
from app.config.settings import settings
from app.utils.auth import verify_token, optional_verify_token
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def create_trip(request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path="/trips",
        method="POST",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.get("")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def list_trips(request: Request, token_payload: Optional[dict] = Depends(optional_verify_token)):
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path="/trips",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]

@router.get("/{trip_id}")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def get_trip(trip_id: str, request: Request, token_payload: Optional[dict] = Depends(optional_verify_token)):
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path=f"/trips/{trip_id}",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]

@router.post("/{trip_id}/coordinates")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def add_coordinate(trip_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path=f"/trips/{trip_id}/coordinates",
        method="POST",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.put("/{trip_id}/complete")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def complete_trip(trip_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path=f"/trips/{trip_id}/complete",
        method="PUT",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]
