from fastapi import APIRouter, Request, Depends
from typing import Optional
from app.services.proxy import proxy
from app.config.settings import settings
from app.utils.auth import verify_token, optional_verify_token
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/paths", tags=["Paths"])

@router.post("/manual")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def create_manual_path(request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path="/paths/manual",
        method="POST",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.get("/search")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def search_paths(request: Request, token_payload: Optional[dict] = Depends(optional_verify_token)):
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path="/paths/search",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]

@router.get("/{path_id}")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def get_path(path_id: str, request: Request, token_payload: Optional[dict] = Depends(optional_verify_token)):
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path=f"/paths/{path_id}",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]
