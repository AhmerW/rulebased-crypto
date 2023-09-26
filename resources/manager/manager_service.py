import typing

from core.config import logger, ShariaCryptoCheckerAPP
from resources.modules.sharia.sharia_service import ShariaService
from resources.data.data_service import checkpointService as cps


class Modules:
    Sharia = "sharia_module"


class ModuleManagerService:
    def __init__(self):
        self.modules = {
            Modules.Sharia: ShariaService(),
        }

    async def _set_cp_active(self, cpid, value):
        cp = await cps.get_checkpoint(cpid)
        cp.active = value
        await cps.add_checkpoint(cpid, cp)

    def get_module(self, module: Modules):
        if module in self.modules:
            return self.modules.get(module)[0]

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
        for module, mo in self.modules.items():
            checkpoint = await cps.get_checkpoint(module)
            logger.info(
                f"Found module {module} - Status (active) = {checkpoint.active}"
            )
            if checkpoint.active:
                await mo.start()


class ManagerService:
    def __init__(self):
        self.module_manager = ModuleManagerService()

    async def start(self):
        await self.module_manager.load_modules()


managerService: typing.Final[ManagerService] = ManagerService()


@ShariaCryptoCheckerAPP.on_event("startup")
async def startup_service():
    await managerService.start()
