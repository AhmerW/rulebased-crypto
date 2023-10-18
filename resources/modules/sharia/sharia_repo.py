import asyncio
import typing

import aiohttp
import re

from pandas.io.json._normalize import nested_to_record


URL = "https://api.coingecko.com/api/v3/coins/{coin}?localization=false&tickers=false&market_data=false&community_data=false&developer_data=false&sparkline=false"

TARGETS = [
    "chat_url",
    "announcement_url",
    "facebook_username",
    "subreddit_url",
    "repos_url",
    "official_forum_url",
    "websites",
    "links",
]

TARGET_STR = ["http", ".com", ".app", "://", "www"]


class ShariaRepo:
    async def run_sharia_check(self, links, words):
        async with aiohttp.ClientSession() as session:
            for link in links:
                print(f"Checking {link}")
                try:
                    response = await session.get(
                        link,
                        allow_redirects=False,
                        timeout=5,
                    )
                    text = await response.text()
                    print(f"response: {len(text)}")
                    text = text.lower()
                    contained: typing.List[typing.Tuple] = [
                        (word, word.lower() in text) for word in words
                    ]
                    if any(x[1] for x in contained):
                        contains = [x[0] for x in contained if x[1]]
                        print(f"Contains: {contains}")
                        return contains
                    print("doesnt contain")
                except asyncio.TimeoutError:
                    continue
        return False

    async def get_crypto_links(self, crypto):
        cid = crypto.get("id")
        url = URL.format(coin=cid)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                harvested_dict = nested_to_record(data)
                harvested = [
                    x
                    if isinstance(x, str)
                    else " , ".join([y for y in x if isinstance(y, str)])
                    if isinstance(x, list)
                    else " , "
                    for x in harvested_dict.values()
                ]
                text = " , ".join(
                    [h for h in harvested if any(x in h for x in TARGET_STR)]
                )
                links = re.findall(
                    "((www\.|http://|https://)(www\.)*.*?(?=(www\.|http://|https://|$)))",
                    text,
                )
                links = [x[0].replace(",", "").strip() for x in links]
                print(links)
            return links

    async def get_crypto_list(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.coingecko.com/api/v3/coins/list?include_platform=false"
            ) as response:
                data = await response.json()
                print(data[0:10])
        return data

    async def clear_from_scamlist(self, data):
        # check for scams
        return data
