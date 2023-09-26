from random import choice, randint


class ShariaRepo:
    async def get_crypto_list(self):
        return [
            {
                "symbol": "".join([choice("abcdefghijklmnopqrtuv") for _ in range(3)]),
                "rank": randint(0, 100),
            }
            for _ in range(5)
        ]

    async def clear_from_scamlist(self, data):
        # check for scams
        return data
