import asyncio
from core.config import logger
from resources.data.data_service import dataService, DataFiles, get_data_file


class ModuleSettings:
    def __init__(self, settings: dict, default=None, file=None):
        self._settings = settings
        self._default = default if default else {}
        self._file = file if file else DataFiles.settings_json

    async def save(self):
        await dataService.save_data(self._file, self._settings)

    async def update(self, key, value):
        self._settings[key] = value
        await self.save()

    async def update_list(self, initial, key, value):
        if isinstance(self._settings.get(initial), list):
            self._settings[initial][key] = value
            await self.save()

    def get_all(self):
        return self._settings

    def get_safe(self, key, default=None):
        # returns from default if not found in settings
        # and if not found in default either returns the parameter
        if (value := self._settings.get(key)) is not None:
            return value
        return self._default.get(key, default)

    def get(self, key, default=None):
        return self._settings.get(key, default)


class BaseModule:
    def __init__(
        self,
        name: str,
        active: bool = True,
    ):
        self.name = name
        self._active = active
        self.settings = ModuleSettings({})
        self.status = {}

    def update_status(self, key, value):
        self.status[key] = value

    def get_status(self, key=None, default=None):
        if key is None:
            return self.status
        return self.status.get(key, default)

    async def load_settings(self):
        settings = {}
        file = get_data_file(self.name)
        if hasattr(self, "default_settings"):
            settings = self.default_settings

        file_settings = await dataService.get_data(file)
        # prioritize json over default_settings
        if file_settings:
            logger.info(f"[{self.name}] Loaded settings from file")
            settings = file_settings
        else:
            logger.info(f"[{self.name}] Loaded default settings")
            await dataService.save_data(file, settings)

        self.settings = ModuleSettings(settings, file=file)

    async def deactivate(self):
        logger.warning(f"Deactivating module {self.__class__.__name__}")
        self._active = False
        await self.settings.update("active", self._active)

    async def activate(self, *args, **kwargs):
        logger.warning(f"Activating module {self.__class__.__name__}")
        self._active = True

        if hasattr(self, "start") and callable(self.start):
            await self.start(**kwargs)

    async def start(self, *args, **kwargs):
        raise NotImplementedError()

    def is_active(self) -> bool:
        return self._active
