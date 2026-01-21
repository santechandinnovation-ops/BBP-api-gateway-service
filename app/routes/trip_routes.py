from fastapi import APIRouter, Request, Depends
from typing import Optional
from app.services.proxy import proxy
from app.config.settings import settings
from app.utils.auth import verify_token, optional_verify_token
from app.utils.response_helper import create_response_from_proxy
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
    return create_response_from_proxy(response)

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
    return create_response_from_proxy(response)

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
    return create_response_from_proxy(response)

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
    return create_response_from_proxy(response)


@router.post("/{trip_id}/coordinates/batch")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def add_coordinates_batch(trip_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    """Add multiple coordinates in a single request (used when stopping a trip)."""
    body = await request.json()
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path=f"/trips/{trip_id}/coordinates/batch",
        method="POST",
        headers=dict(request.headers),
        body=body
    )
    return create_response_from_proxy(response)


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
    return create_response_from_proxy(response)


@router.delete("/{trip_id}")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def delete_trip(trip_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    """Delete a trip and all its associated data."""
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path=f"/trips/{trip_id}",
        method="DELETE",
        headers=dict(request.headers)
    )
    return create_response_from_proxy(response)
