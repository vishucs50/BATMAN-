"""
COA Router — BATMAN Gateway (Proxy to batman-planning-svc)
"""
from fastapi import APIRouter, Request, Response
import httpx
from ..config import Settings

router = APIRouter(prefix="/coa")
settings = Settings()
PLANNING_URL = settings.PLANNING_SVC_URL

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_coa(path: str, request: Request):
    url = f"{PLANNING_URL}/planning/coa/{path}"
    async with httpx.AsyncClient() as client:
        # Pass headers, params, and body
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
