from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.responses import ApiResponse
from app.db.session import get_db


router = APIRouter()


class HealthData(BaseModel):
    status: Literal["UP"] = "UP"
    service: str


class DatabaseHealthData(BaseModel):
    status: Literal["UP"] = "UP"
    database: str


@router.get("/health", response_model=ApiResponse[HealthData])
def health_check() -> ApiResponse[HealthData]:
    return ApiResponse.success(
        HealthData(service="certificate-evidence-backend")
    )


@router.get("/health/db", response_model=ApiResponse[DatabaseHealthData])
def database_health_check(
    db: Session = Depends(get_db),
) -> ApiResponse[DatabaseHealthData]:
    database_name = db.execute(text("select database()")).scalar_one()
    return ApiResponse.success(
        DatabaseHealthData(database=database_name)
    )