import typing
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.exceptions import HTTPException
from resources.manager.manager_service import managerService
from resources.modules.base import BaseModule

router = APIRouter()


async def get_module(module: str):
    module = managerService.module_manager.get_module(module)
    if not module:
        raise HTTPException(400)
    return module


async def get_admin(access_key: str) -> bool:
    a = access_key == "123"
    if not a:
        raise HTTPException(400)

    return a


@router.get("/{module}/deactivate")
async def deactivate_module(
    module: BaseModule = Depends(get_module), access: bool = Depends(get_admin)
) -> bool:
    await module.deactivate()
    return not module.is_active()


@router.get("/{module}/activate")
async def activate_module(
    module: BaseModule = Depends(get_module), _: bool = Depends(get_admin)
) -> bool:
    await module.activate()
    return module.is_active()


@router.get("/{module}/status")
async def get_module_status(
    status: str = None, module: BaseModule = Depends(get_module)
) -> typing.Any:
    return module.get_status(
        status,
    )


@router.get("/{module}/settings")
async def get_module_settings(module: BaseModule = Depends(get_module)) -> dict:
    return module.settings.get_all()


@router.post("/{module}/settings")
async def update_module_settings(
    key: str,
    value: str,
    module: BaseModule = Depends(get_module),
    _: bool = Depends(get_admin),
    list_key=None,
):
    # {key: value} if not list_key else {key: {list_key: [+value]}
    await managerService.update_module_settings(module, key, value, list_key)
