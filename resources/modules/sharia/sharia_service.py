import asyncio
from core.config import logger
from resources.data.data_service import checkpointService as cps
from resources.data.data_service import dataService, DataFiles
from resources.modules.base import BaseModule
from resources.modules.sharia.sharia_repo import ShariaRepo
from resources.data.data_models import Checkpoint


class CheckUrls:
    coin_data_url = (
        "https://api.coingecko.com/api/v3/coins/"
        "{coin_id}?localization=false&tickers=false&market_data=false&community_data=false&developer_data"
        "=false&sparkline=false"
    )


class ShariaStatus:
    current_index = "current_index"
    current_crypto = "current_crypto"
    remaining = "remaining"
    active = "active"


class ShariaService(BaseModule):
    module = "sharia_module"
    # in seconds
    # checkpoint_interval: save a checkpoint after x coins
    default_settings = {"scheduled_interval": 20, "checkpoint_save_interval": 50}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_sharia_checks(self) -> list:
        # Returns a list of those already checked
        data = await dataService.get_data(DataFiles.data_json)
        return [x for x in data.get("crypto", []) if (x.get("compliant") is not None)]

    async def run_single_check(self, crypto, repo=None, index=None):
        # Runs a single check on a single crypto
        repo = repo if repo else ShariaRepo()

        links = await repo.get_crypto_links(crypto)
        words = self.settings.get_safe("words", [])
        check = await repo.run_sharia_check(links, words)

        if check and index:
            await dataService.update_index(
                DataFiles.data_json,
                "crypto",
                index,
                "compliant",
                False,
            )
            logger.info(f"{self.name} {crypto.get('symbol')} failed the sharia check")

        return bool(check)

    async def update_data_db(self):
        # get all coins
        # check if in scamlist
        # save only name, symbol, and required compare data
        # get compare_data from params_service
        # compare_data = ["market_ranking"] <- can be updated dynamically from UI (manager)
        #
        # then update db file
        crypto = await ShariaRepo().get_crypto_list()
        await dataService.save_data(DataFiles.data_json, {"crypto": crypto})

    async def start_checking(self, checkpoint: Checkpoint, wait_ts=0):
        logger.info(f"Waiting {wait_ts} seconds. ({round(wait_ts / 60, 2)} minutes)")
        await asyncio.sleep(wait_ts)
        # first update the data db
        await self.update_data_db()
        data = await dataService.get_data(DataFiles.data_json)
        data = data.get("crypto", [])
        save_interval = self.settings.get_safe("checkpoint_save_interval", 0)

        logger.info(
            f"Starting {self.__class__.__name__} from position {checkpoint.position} ({checkpoint.position}/{len(data)})"
        )

        if len(data) > checkpoint.position:
            data = data[checkpoint.position : -1]

        repo = ShariaRepo()

        # enumerate maintains the buffered file reading !
        for i, line in enumerate(data):
            # save checkpoint
            if ((i % save_interval) == 0) or (not self.is_active()):
                logger.info(
                    f"[{self.name}] Saving checkpoint at position {checkpoint.position + i}"
                )
                await cps.add_checkpoint(
                    cps.checkpoint_id(self.name, "checkpoint"), Checkpoint(position=i)
                )
                await asyncio.sleep(1)

            # update status
            self.update_status(ShariaStatus.remaining, len(data) - i)
            self.update_status(ShariaStatus.current_index, i)
            self.update_status(ShariaStatus.current_crypto, line)
            self.update_status(ShariaStatus.active, self.is_active())

            if not self.is_active():
                return

            # run check
            await self.run_single_check(line, repo, index=i)

            # wait a bit
            await asyncio.sleep(5)

        # done checking? save checkpoint.
        logger.info(f"[{self.name}] Checking done. Resetting checkpoint.")
        await cps.add_checkpoint(
            cps.checkpoint_id(self.name, "checkpoint"), Checkpoint(position=0)
        )

    async def start(self):
        # Start the checking process
        # This should be on a background task

        # last time checked info
        checkpoint = await cps.get_checkpoint(
            cps.checkpoint_id(self.name, "checkpoint")
        )
        if not checkpoint.active:
            return

        logger.info(f"Starting Module {self.__class__.__name__}")
        scheduled_interval = self.settings.get_safe("scheduled_interval", 0)
        logger.info(
            f"Module {self.__class__.__name__} Scheduled for {scheduled_interval} - Checkpoint: {checkpoint}"
        )

        data = await dataService.get_data(DataFiles.data_json)
        save_interval = self.settings.get_safe("checkpoint_save_interval", 0)
        if isinstance(data, dict):
            data = data.get("crypto", [])
            did_finish = save_interval != 0 and save_interval == len(data)
        else:
            did_finish = True

        logger.info(
            f"Module {self.__class__.__name__} {'did not finish' if not did_finish else 'finished'} on last check {save_interval} / {len(data)}"
        )

        await asyncio.gather(
            self.start_checking(
                checkpoint,
                wait_ts=0
                if (
                    not did_finish
                    or not cps.is_time(checkpoint.check_dt, scheduled_interval)
                )
                else cps.get_sec_diff(checkpoint.check_dt, interval=scheduled_interval),
            ),
        )
