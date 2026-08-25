from fastapi import FastAPI

from app.api.costs import router as costs_router
from app.api.health import router as health_router
from app.api.images import router as images_router


app = FastAPI(
    title="AI Image Relevance Engine",
    version="0.2.0",
)

app.include_router(health_router)
app.include_router(images_router)
app.include_router(costs_router)