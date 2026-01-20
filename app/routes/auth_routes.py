from fastapi import APIRouter, Request
from app.services.proxy import proxy
from app.config.settings import settings
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
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
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
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
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def logout_user(request: Request):
    response = await proxy.forward_request(
        service_name="user-service",
        service_url=settings.USER_SERVICE_URL,
        path="/auth/logout",
        method="POST",
        headers=dict(request.headers)
    )
    return response["content"]
