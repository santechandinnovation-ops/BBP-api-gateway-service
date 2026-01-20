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

            print(f"[CIRCUIT BREAKER DEBUG] Service: {service_name}, Status: {response.status_code}, Railway Down: {is_railway_not_found}")

            if is_railway_not_found or response.status_code >= 500:
                print(f"[CIRCUIT BREAKER] Recording FAILURE for {service_name} (status={response.status_code}, railway_down={is_railway_not_found})")
                circuit_breaker.record_failure(service_name)
            elif 200 <= response.status_code < 500:
                print(f"[CIRCUIT BREAKER] Recording SUCCESS for {service_name} (status={response.status_code})")
                circuit_breaker.record_success(service_name)
            else:
                print(f"[CIRCUIT BREAKER] Recording FAILURE for {service_name} (unexpected status={response.status_code})")
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

        print(f"[RAILWAY CHECK] status={status}, is_json={is_json}, type(content)={type(content)}, content_type={content_type}")
        print(f"[RAILWAY CHECK] content={content}")

        if is_json and isinstance(content, dict):
            detail = content.get("detail")
            print(f"[RAILWAY CHECK] Found detail field: '{detail}'")

            if detail == "Not Found":
                print(f"[RAILWAY CHECK] MATCH: detail == 'Not Found' (Railway generic error) -> Service is DOWN")
                return True

            if not detail or detail == "":
                print(f"[RAILWAY CHECK] MATCH: Empty or missing detail -> Service is DOWN")
                return True

            message = content.get("message", "").lower()
            print(f"[RAILWAY CHECK] Checking message field: '{message}'")
            if message and any(phrase in message for phrase in [
                "application not found",
                "service not found",
                "not deployed",
                "not found"
            ]):
                print(f"[RAILWAY CHECK] MATCH: message contains service down phrase -> Service is DOWN")
                return True

            if len(content) == 1 and "detail" in content and isinstance(detail, str) and len(detail) < 50:
                print(f"[RAILWAY CHECK] MATCH: Simple generic error (single 'detail' field) -> Service is DOWN")
                return True

        if not is_json:
            print(f"[RAILWAY CHECK] Non-JSON content with 404")
            if "text/html" in content_type.lower():
                print(f"[RAILWAY CHECK] MATCH: HTML response -> Service is DOWN")
                return True
            if not content or (isinstance(content, str) and len(content.strip()) < 100):
                print(f"[RAILWAY CHECK] MATCH: Empty or very short text response -> Service is DOWN")
                return True

        print(f"[RAILWAY CHECK] NO MATCH: Treating as legitimate 404 from running service")
        return False

    async def close(self):
        await self.client.aclose()

proxy = ServiceProxy()
