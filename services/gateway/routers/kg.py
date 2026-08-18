"""
Knowledge Graph Router — BATMAN Gateway (Proxy to batman-kg-svc)
"""
from fastapi import APIRouter, Request, Response
import httpx
from ..config import Settings

router = APIRouter(prefix="/kg")
settings = Settings()
KG_URL = settings.KG_SVC_URL

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_kg(path: str, request: Request):
    url = f"{KG_URL}/kg/{path}"
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
