from fastapi import FastAPI

from app.api.v1.missions import router as missions_router
from app.api.v1.objectives import router as objectives_router

app = FastAPI(
    title="BATMAN Backend",
    version="0.1.0",
)


app.include_router(
    missions_router,
    prefix="/api/v1",
)
app.include_router(
    objectives_router,
    prefix="/api/v1",
)

@app.get("/")
def home():
    return {
        "message": "BATMAN backend is running"
    }