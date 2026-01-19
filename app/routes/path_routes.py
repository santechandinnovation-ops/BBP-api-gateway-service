from fastapi import APIRouter, Request, Depends
from typing import Optional
from app.services.proxy import proxy
from app.config.settings import settings
from app.utils.auth import verify_token, optional_verify_token

router = APIRouter(prefix="/api/paths", tags=["Paths"])

@router.post("")
async def create_path(request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path="/api/paths",
        method="POST",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.get("")
async def list_paths(request: Request, token_payload: Optional[dict] = Depends(optional_verify_token)):
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path="/api/paths",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]

@router.get("/search")
async def search_paths(request: Request, token_payload: Optional[dict] = Depends(optional_verify_token)):
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path="/api/paths/search",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]

@router.get("/{path_id}")
async def get_path(path_id: str, request: Request, token_payload: Optional[dict] = Depends(optional_verify_token)):
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path=f"/api/paths/{path_id}",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]

@router.put("/{path_id}")
async def update_path(path_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path=f"/api/paths/{path_id}",
        method="PUT",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.delete("/{path_id}")
async def delete_path(path_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path=f"/api/paths/{path_id}",
        method="DELETE",
        headers=dict(request.headers)
    )
    return response["content"]

@router.post("/{path_id}/obstacles")
async def add_obstacle(path_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    body = await request.json()
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path=f"/api/paths/{path_id}/obstacles",
        method="POST",
        headers=dict(request.headers),
        body=body
    )
    return response["content"]

@router.get("/{path_id}/obstacles")
async def get_obstacles(path_id: str, request: Request, token_payload: Optional[dict] = Depends(optional_verify_token)):
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path=f"/api/paths/{path_id}/obstacles",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]

@router.get("/user/{user_id}")
async def get_user_paths(user_id: str, request: Request, token_payload: dict = Depends(verify_token)):
    response = await proxy.forward_request(
        service_name="path-service",
        service_url=settings.PATH_SERVICE_URL,
        path=f"/api/paths/user/{user_id}",
        method="GET",
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    return response["content"]
