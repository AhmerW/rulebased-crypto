import asyncio
from core.config import logger


class BaseModule:
    def __init__(
        self,
        active: bool = True,
    ):
        self._active = active

    def deactivate(self):
        logger.warning(f"Deactivating module {self.__class__.__name__}")
        self._active = False

    def activate(self, *args, **kwargs):
        logger.warning(f"Activating module {self.__class__.__name__}")
        self._active = True
        if hasattr(self, "start") and callable(self.start):
            self.start(*args, **kwargs)

    def is_active(self) -> bool:
        return self._active
