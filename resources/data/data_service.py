from typing import Optional, Final
from datetime import datetime, timedelta

from resources.data.data_models import Checkpoint
from resources.data.data_repo import DataRepo, DataFiles, get_data_file


class CheckpointService:
    def checkpoint_id(self, prefix, id):
        # to distinguish between other modules in the same checkpoint files
        return f"{prefix}_{id}"

    async def add_checkpoint(self, checkpoint_id: str, cp: Checkpoint):
        repo = DataRepo(DataFiles.checkpoint_json)
        async with repo.file_op() as f:
            data = await repo.get_from_datafile(f)
            data[checkpoint_id] = cp.model_dump()
            await repo.write_to_datafile(data)

    async def get_checkpoint(
        self,
        checkpoint_id: str,
        notnull=True,
    ) -> Optional[Checkpoint]:
        blob = await DataRepo(
            DataFiles.checkpoint_json,
        ).get_from_datafile()
        if isinstance(blob, dict):
            data = blob.get(checkpoint_id, None)
            if data:
                return Checkpoint(**data)

        if notnull:
            checkpoint = Checkpoint()
            await self.add_checkpoint(checkpoint_id, checkpoint)
            return checkpoint

    @staticmethod
    def is_time(dt: datetime, interval: int = 0) -> int:
        return (dt + timedelta(seconds=interval)) >= dt.now()

    @staticmethod
    def get_sec_diff(dt, dt2=None, interval: int = 0) -> int:
        dt2 = dt2 if dt2 else datetime.now()
        dt += timedelta(seconds=interval)
        return (dt - dt2).seconds

    @staticmethod
    def dt_now_plus(self, *args, **kwargs):
        return datetime.now() + timedelta(*args, **kwargs)


class DataService:
    async def save_data(self, file, data):
        return await DataRepo(file).write_to_datafile(data)

    async def get_data(self, file):
        return await DataRepo(file).get_from_datafile()

    async def update_index(self, file, initial, index, key, value):
        repo = DataRepo(file)
        data = await repo.get_from_datafile()  # dict
        l = data.get(initial, [])  # list
        if len(l) > index:
            if isinstance(l[index], dict):  # dict
                data[initial][index][key] = value

        await repo.write_to_datafile(data)

    async def update(self):
        pass


checkpointService: Final[CheckpointService] = CheckpointService()
dataService: Final[DataService] = DataService()
