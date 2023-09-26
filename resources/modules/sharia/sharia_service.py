import asyncio

from core.config import logger
from resources.data.data_service import checkpointService as cps
from resources.data.data_service import dataService, DataFiles
from resources.modules.base import BaseModule
from resources.modules.sharia.sharia_repo import ShariaRepo


class CheckUrls:
    coin_data_url = (
        "https://api.coingecko.com/api/v3/coins/"
        "{coin_id}?localization=false&tickers=false&market_data=false&community_data=false&developer_data"
        "=false&sparkline=false"
    )


class ShariaService(BaseModule):
    module = "sharia_module"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_next_to_check(self):
        # Gets next to check. It is different from get_last_checkpoint,
        # as the latter will return the last that HAS been checked.
        pass

    async def create_checkpoint(self):
        pass

    async def mark_checked(self):
        # Mark a crypto as "checked"
        pass

    async def get_already_checked(self, pagination: int):
        # Returns a list of those already checked
        pass

    async def run_single_check(self):
        # Runs a single check on a single crypto
        pass

    async def update_data_db(self):
        pass
        # get all coins
        # check if in scamlist
        # save only name, symbol, and required compare data
        # get compare_data from params_service
        # compare_data = ["market_ranking"] <- can be updated dynamically from UI (manager)
        #
        # then update db file
        crypto = await ShariaRepo().get_crypto_list()
        await dataService.save_data(DataFiles.data_json, crypto)

    async def start_checking(self, wait_ts=0):
        logger.info(f"Waiting {wait_ts / 60} minutes.")
        await asyncio.sleep(wait_ts)
        # first update the data db
        await self.update_data_db()

    async def start(self):
        # Start the checking process
        # This should be on a background task

        # last time checked info
        checkpoint = await cps.get_checkpoint("checkpoint")
        if not checkpoint.active:
            return
        logger.info(f"Starting Module {self.__class__.__name__}")

        await asyncio.gather(
            self.start_checking(
                wait_ts=0
                if not cps.is_time(checkpoint.check_dt)
                else cps.get_sec_diff(checkpoint.check_dt)
            ),
        )
