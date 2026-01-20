from fastapi import APIRouter, Request
from app.services.proxy import proxy
from app.config.settings import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register_user(request: Request):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="user-service",
        service_url=settings.USER_SERVICE_URL,
        path="/auth/register",
        method="POST",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.post("/login")
async def login_user(request: Request):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="user-service",
        service_url=settings.USER_SERVICE_URL,
        path="/auth/login",
        method="POST",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.post("/logout")
async def logout_user(request: Request):
    response = await proxy.forward_request(
        service_name="user-service",
        service_url=settings.USER_SERVICE_URL,
        path="/auth/logout",
        method="POST",
        headers=dict(request.headers)
    )
    return response["content"]
