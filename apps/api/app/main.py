from fastapi import FastAPI

from app.config import settings
from app.routers import ce_features, decision_records, health

app = FastAPI(
    title="DevOpsLedger API",
    version="1.2.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
)

app.include_router(health.router, tags=["system"])
app.include_router(decision_records.router, tags=["decision-records"])
app.include_router(ce_features.router, tags=["community-edition"])
