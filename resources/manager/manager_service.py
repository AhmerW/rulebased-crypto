import typing
import asyncio
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


from core.config import logger, ShariaCryptoCheckerAPP
from resources.modules.sharia.sharia_service import ShariaService
from resources.data.data_service import checkpointService as cps
from resources.modules.base import BaseModule

T = typing.TypeVar("T", bound=BaseModule)


class Modules:
    Sharia: str = "sharia_module"


class ModuleManagerService:
    def __init__(self):
        # All modules
        self.modules: typing.Dict[str, typing.Type[T]] = {
            Modules.Sharia: ShariaService(Modules.Sharia),
        }

    async def _set_cp_active(self, cpid, value):
        cp = await cps.get_checkpoint(cpid)
        cp.active = value
        await cps.add_checkpoint(cpid, cp)

    @typing.overload
    def get_module(self, module: Modules.Sharia) -> ShariaService:
        return self.modules.get(Modules.Sharia)

    def get_module(self, module: typing.Type[T]) -> T:
        if module in self.modules:
            return self.modules.get(module)

    async def start_module(self, module):
        await self._set_cp_active(module, True)
        if module in self.modules:
            # module object
            mo = self.modules[module]
            mo.active = True
            await mo.start()

    async def stop_module(self, module):
        await self._set_cp_active(module, False)
        mo = self.modules[module]
        mo.active = False

    async def load_modules(self):
        mo: BaseModule
        for module, mo in self.modules.items():
            await mo.load_settings()
            active = mo.settings.get_safe("active", True)
            logger.info(f"Found module {module} - Status (active) = {active}")
            if active:
                t = threading.Thread(target=asyncio.run, args=(mo.start(),))
                t.start()


class ManagerService:
    def __init__(self):
        self.module_manager = ModuleManagerService()

    async def start(self):
        await self.module_manager.load_modules()

    async def update_module_settings(self, module, key, value, list_key=None):
        module = self.module_manager.get_module(module)
        if not module:
            return

        if list_key:
            await module.settings.update_list(list_key, key, value)
        else:
            await module.settings.update(key, value)

    async def get_module_settings(self, module):
        module = self.module_manager.get_module(module)
        if module:
            return module.settings

        return {}


managerService: typing.Final[ManagerService] = ManagerService()


@ShariaCryptoCheckerAPP.on_event("startup")
async def startup_service():
    await managerService.start()
