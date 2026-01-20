from fastapi import APIRouter, Request, Depends
from typing import Optional
from app.services.proxy import proxy
from app.config.settings import settings
from app.utils.auth import verify_token, optional_verify_token

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile")
async def get_profile(request: Request, token_payload: dict = Depends(verify_token)):
    response = await proxy.forward_request(
        service_name="user-service",
        service_url=settings.USER_SERVICE_URL,
        path="/users/profile",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]

@router.put("/profile")
async def update_profile(request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="user-service",
        service_url=settings.USER_SERVICE_URL,
        path="/users/profile",
        method="PUT",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.get("/{user_id}")
async def get_user(user_id: str, request: Request, token_payload: Optional[dict] = Depends(optional_verify_token)):
    response = await proxy.forward_request(
        service_name="user-service",
        service_url=settings.USER_SERVICE_URL,
        path=f"/users/{user_id}",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]
