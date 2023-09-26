from typing import Optional, Final
from datetime import datetime, timedelta

from resources.data.data_models import Checkpoint
from resources.data.data_repo import DataRepo, DataFiles


class CheckpointService:
    async def add_checkpoint(self, checkpoint_id: str, cp: Checkpoint):
        repo = DataRepo(DataFiles.data_json)
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
    def is_time(dt: datetime) -> int:
        return datetime.now() >= dt

    @staticmethod
    def get_sec_diff(dt, dt2=None) -> int:
        dt2 = dt2 if dt2 else datetime.now()
        return (dt2 - dt).seconds

    @staticmethod
    def dt_now_plus(self, *args, **kwargs):
        return datetime.now() + timedelta(*args, **kwargs)


class DataService:
    async def save_data(self, file, data):
        await DataRepo(file).write_to_datafile(data)


checkpointService: Final[CheckpointService] = CheckpointService()
dataService: Final[DataService] = DataService()
