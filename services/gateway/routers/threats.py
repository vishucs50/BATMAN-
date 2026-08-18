"""
Threats Router — BATMAN Gateway (Proxy to batman-threat-svc)
"""
from fastapi import APIRouter, Request, Response
import httpx
from ..config import Settings

router = APIRouter(prefix="/threats")
settings = Settings()
THREAT_URL = settings.THREAT_SVC_URL

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_threats(path: str, request: Request):
    url = f"{THREAT_URL}/threats/{path}"
    async with httpx.AsyncClient() as client:
        req_headers = dict(request.headers)
        req_headers.pop("host", None)
        
        body = await request.body()
        resp = await client.request(
            request.method,
            url,
            headers=req_headers,
            params=request.query_params,
            content=body
        )
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
