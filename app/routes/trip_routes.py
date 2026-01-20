from fastapi import APIRouter, Request, Depends
from typing import Optional
from app.services.proxy import proxy
from app.config.settings import settings
from app.utils.auth import verify_token, optional_verify_token

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("")
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

@router.put("/{trip_id}")
async def update_trip(trip_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path=f"/trips/{trip_id}",
        method="PUT",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.delete("/{trip_id}")
async def delete_trip(trip_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path=f"/trips/{trip_id}",
        method="DELETE",
        headers=dict(request.headers)
    )
    return response["content"]

@router.post("/{trip_id}/start")
async def start_trip(trip_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json() if request.headers.get("content-length") else None
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path=f"/trips/{trip_id}/start",
        method="POST",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.post("/{trip_id}/complete")
async def complete_trip(trip_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json() if request.headers.get("content-length") else None
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path=f"/trips/{trip_id}/complete",
        method="POST",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.get("/user/{user_id}")
async def get_user_trips(user_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    response = await proxy.forward_request(
        service_name="trip-service",
        service_url=settings.TRIP_SERVICE_URL,
        path=f"/trips/user/{user_id}",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]
