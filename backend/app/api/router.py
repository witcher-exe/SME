from fastapi import APIRouter
from app.api.data_ingestion import router as data_router
from app.api.dashboard import router as dashboard_router
from app.api.forecast import router as forecast_router
from app.api.financing import router as financing_router
from app.api.operations import router as operations_router
from app.api.governance import router as governance_router
from app.api.chat import router as chat_router

api_router = APIRouter(prefix="/api")

api_router.include_router(data_router)
api_router.include_router(dashboard_router)
api_router.include_router(forecast_router)
api_router.include_router(financing_router)
api_router.include_router(operations_router)
api_router.include_router(governance_router)
api_router.include_router(chat_router)
