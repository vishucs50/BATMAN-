"""
AAR Router — BATMAN Gateway (Proxy to batman-wargame-svc)
"""
from fastapi import APIRouter, Request, Response
import httpx
from ..config import Settings

router = APIRouter(prefix="/aar")
settings = Settings()
WARGAME_URL = settings.WARGAME_SVC_URL

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_aar(path: str, request: Request):
    target_path = f"/wargame/aar/{path}" if path else "/wargame/aar"
    url = f"{WARGAME_URL}{target_path}"
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

@router.get("")
@router.get("/")
async def proxy_aar_root(request: Request):
    url = f"{WARGAME_URL}/wargame/aar"
    async with httpx.AsyncClient() as client:
        req_headers = dict(request.headers)
        req_headers.pop("host", None)
        
        resp = await client.request(
            "GET",
            url,
            headers=req_headers,
            params=request.query_params
        )
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
