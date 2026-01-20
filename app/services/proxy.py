import httpx
from fastapi import HTTPException
from typing import Optional, Any
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

            filtered_headers = {
                k: v for k, v in (headers or {}).items()
                if k.lower() not in {'host', 'content-length'}
            }

            response = await self.client.request(
                method=method,
                url=url,
                headers=filtered_headers,
                json=body,
                params=query_params
            )

            content: Any = None
            is_json = False
            try:
                if response.content:
                    content = response.json()
                    is_json = True
            except Exception:
                content = response.text

            is_railway_not_found = self._is_railway_service_down(
                response.status_code,
                content,
                is_json,
                response.headers.get("content-type", "")
            )

            if is_railway_not_found or response.status_code >= 500:
                circuit_breaker.record_failure(service_name)
            elif 200 <= response.status_code < 500:
                circuit_breaker.record_success(service_name)
            else:
                circuit_breaker.record_failure(service_name)

            return {
                "status_code": response.status_code,
                "content": content,
                "headers": dict(response.headers)
            }

        except httpx.TimeoutException:
            circuit_breaker.record_failure(service_name)
            raise HTTPException(status_code=504, detail=f"{service_name} service timeout")

        except httpx.RequestError:
            circuit_breaker.record_failure(service_name)
            raise HTTPException(status_code=502, detail=f"{service_name} service unavailable")

        except Exception:
            circuit_breaker.record_failure(service_name)
            raise HTTPException(
                status_code=500,
                detail=f"Error communicating with {service_name} service"
            )

    def _is_railway_service_down(
        self,
        status: int,
        content: Any,
        is_json: bool,
        content_type: str
    ) -> bool:
        if status != 404:
            return False

        print(f"DEBUG RAILWAY CHECK: status={status}, is_json={is_json}, content={content}, type(content)={type(content)}")

        if is_json and isinstance(content, dict):
            detail = content.get("detail")
            if detail == "Not Found":
                return True

            message = content.get("message", "").lower()
            if any(phrase in message for phrase in [
                "application not found",
                "service not found",
                "not deployed"
            ]):
                return True

        if not content or not is_json:
            if "text/html" in content_type.lower() or not content:
                return True

        return False

    async def close(self):
        await self.client.aclose()

proxy = ServiceProxy()
