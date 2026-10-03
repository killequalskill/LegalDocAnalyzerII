from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.documents import router as documents_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.search import router as search_router
from app.api.routes.qa import router as qa_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(documents_router)
api_router.include_router(analysis_router)
api_router.include_router(search_router)
api_router.include_router(qa_router)
