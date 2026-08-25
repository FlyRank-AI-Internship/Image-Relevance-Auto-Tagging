from fastapi import FastAPI

from app.api.costs import router as costs_router
from app.api.health import router as health_router
from app.api.images import router as images_router
from app.api.posts import router as posts_router
from app.api.jobs import router as jobs_router
from app.api.reviews import router as reviews_router
from app.api.eval import router as eval_router


app = FastAPI(
    title="AI Image Relevance Engine",
    version="0.3.0",
)

app.include_router(health_router)
app.include_router(images_router)
app.include_router(posts_router)
app.include_router(costs_router)
app.include_router(reviews_router)
app.include_router(jobs_router)
app.include_router(eval_router)