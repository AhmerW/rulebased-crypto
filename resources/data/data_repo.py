from os import path
from contextlib import asynccontextmanager

import aiofiles
import orjson

BASE_DB_PATH = path.join("resources", "data", "db")


class DataFiles:
    checkpoint_json = path.join(BASE_DB_PATH, "checkpoint.json")
    data_json = path.join(BASE_DB_PATH, "data.json")
    settings_json = path.join(BASE_DB_PATH, "settings.json")


def get_data_file(filename):
    return path.join(BASE_DB_PATH, f"{filename}.json")


class DataRepo:
    """Wrapper around aiofiles and json db using orjson"""

    def __init__(self, datafile: str):
        self.datafile = datafile

    async def write_to_datafile(self, data: dict, f=None) -> bool:
        async def _write(fo):
            await fo.write(orjson.dumps(data).decode())
            return True

        if f is not None:
            return await _write(f)

        async with aiofiles.open(self.datafile, "w+") as f:
            return await _write(f)

    async def get_from_datafile(self, f=None) -> dict:
        async def _read(fo):
            return orjson.loads(await f.read())

        try:
            if f is not None:
                return await _read(f)

            async with aiofiles.open(self.datafile) as f:
                return await _read(f)
        except FileNotFoundError:
            await self.write_to_datafile({})
            return {}

    @asynccontextmanager
    async def file_op(self):
        f = await aiofiles.open(self.datafile)
        yield f
        await f.close()
