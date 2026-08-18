"""
GIS Router — BATMAN Gateway (Proxy to batman-gis-svc)
"""
from fastapi import APIRouter, Request, Response
import httpx
from ..config import Settings

router = APIRouter(prefix="/gis")
settings = Settings()
GIS_URL = settings.GIS_SVC_URL

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_gis(path: str, request: Request):
    url = f"{GIS_URL}/gis/{path}"
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
