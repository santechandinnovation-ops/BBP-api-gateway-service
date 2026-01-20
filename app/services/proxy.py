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

            print(f"[CIRCUIT BREAKER DEBUG] Service: {service_name}, Status: {response.status_code}")

            # Logica semplificata: 404 e 5xx = FALLIMENTO, 2xx-3xx = SUCCESSO
            if response.status_code == 404 or response.status_code >= 500:
                print(f"[CIRCUIT BREAKER] Recording FAILURE for {service_name} (status={response.status_code})")
                circuit_breaker.record_failure(service_name)
            elif 200 <= response.status_code < 400:
                print(f"[CIRCUIT BREAKER] Recording SUCCESS for {service_name} (status={response.status_code})")
                circuit_breaker.record_success(service_name)
            else:
                # Altri 4xx (401, 403, ecc.) non influenzano il circuit breaker
                print(f"[CIRCUIT BREAKER] Ignoring status {response.status_code} for circuit breaker (client error)")
                pass

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

    async def close(self):
        await self.client.aclose()

proxy = ServiceProxy()
