# Get recent sharia and update
from fastapi import APIRouter

from core.config import logger

router = APIRouter()


@router.get("/")
async def get_checks():
    logger.info("test")
    return "abc"
