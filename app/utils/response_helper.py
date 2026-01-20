from fastapi import Response
import json
from typing import Any, Dict


def create_response_from_proxy(proxy_response: Dict[str, Any]) -> Response:
    """
    Create a FastAPI Response object from a proxy response dictionary.

    Args:
        proxy_response: Dictionary with 'status_code', 'content', and 'headers'

    Returns:
        FastAPI Response object with proper status code and content
    """
    content = proxy_response["content"]

    if isinstance(content, dict):
        content_str = json.dumps(content)
    elif isinstance(content, str):
        content_str = content
    else:
        content_str = str(content)

    return Response(
        content=content_str,
        status_code=proxy_response["status_code"],
        media_type="application/json"
    )
