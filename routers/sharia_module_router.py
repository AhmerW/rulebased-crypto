from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from resources.manager.manager_service import managerService, Modules
from resources.modules.base import BaseModule
from routers.manager_router import get_module
from resources.modules.sharia.sharia_service import ShariaService

router = APIRouter()


@router.get("/checks")
async def get_checks():
    module = await get_module(Modules.Sharia)
    return await module.get_sharia_checks()


@router.post("/checks")
async def check_one(data: dict) -> bool:
    module: ShariaService = await get_module(Modules.Sharia)
    return await module.run_single_check(data)
