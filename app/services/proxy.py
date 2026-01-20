import httpx
from fastapi import HTTPException, Request
from typing import Optional
from app.config.settings import settings
from app.utils.circuit_breaker import circuit_breaker
class ServiceProxy:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=settings.SERVICE_REQUEST_TIMEOUT)
    async def forward_request(
        self,
        service_name: str,
        service_url: str,
        path: str,
        method: str,
        headers: Optional[dict] = None,
        body: Optional[dict] = None,
        query_params: Optional[dict] = None
    ):
        if not circuit_breaker.can_execute(service_name):
            raise HTTPException(
                status_code=503,
                detail=f"{service_name} service is currently unavailable"
            )
        try:
            url = f"{service_url}{path}"
            filtered_headers = {}
            if headers:
                for key, value in headers.items():
                    if key.lower() not in ['host', 'content-length']:
                        filtered_headers[key] = value
            response = await self.client.request(
                method=method,
                url=url,
                headers=filtered_headers,
                json=body if body else None,
                params=query_params
            )
            response_content = response.json() if response.content else None
            is_service_down = (
                response_content
                and isinstance(response_content, dict)
                and response_content.get("message") == "Application not found"
            )
            if response.status_code >= 500 or is_service_down:
                circuit_breaker.record_failure(service_name)
            else:
                circuit_breaker.record_success(service_name)
            return {
                "status_code": response.status_code,
                "content": response_content,
                "headers": dict(response.headers)
            }
        except httpx.TimeoutException:
            circuit_breaker.record_failure(service_name)
            raise HTTPException(
                status_code=504,
                detail=f"{service_name} service timeout"
            )
        except httpx.RequestError as e:
            circuit_breaker.record_failure(service_name)
            raise HTTPException(
                status_code=502,
                detail=f"{service_name} service unavailable"
            )
        except Exception as e:
            circuit_breaker.record_failure(service_name)
            raise HTTPException(
                status_code=500,
                detail=f"Error communicating with {service_name} service"
            )
    async def close(self):
        await self.client.aclose()
proxy = ServiceProxy()
