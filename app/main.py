from fastapi import FastAPI

from app.api.routes import router as checklist_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(checklist_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
