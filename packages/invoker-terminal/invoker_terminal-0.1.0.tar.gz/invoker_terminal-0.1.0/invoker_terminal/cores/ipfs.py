import logging

import aiohttp
import requests


def status_ipfs(url) -> bool:
    res = requests.get(url)
    return res.status_code == 200


def send_to_ipfs(input: bytes, url: str) -> str:
    logging.info("ipfs post {}".format(url))
    res = requests.post(
        url=url,
        data=input,
        headers={"Content-Type": "application/octet-stream"},
    )
    js = res.json()
    return js["cid"]


def get_from_ipfs(hash: str, url: str) -> bytes:
    urlToGet = "{}/{}".format(url, hash)
    logging.info("ipfs url get {}".format(urlToGet))
    res = requests.get(urlToGet)
    return res.content


async def async_get_from_ipfs(loop, hash: str, url: str) -> bytes:
    async with aiohttp.ClientSession(loop=loop) as session:
        urlToGet = "{}/{}".format(url, hash)
        async with session.get(urlToGet) as response:
            output = await response.read()
            return output


async def async_send_to_ipfs(loop, input: bytes, url: str) -> str:
    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.post(
            url,
            data=input,
            headers={"Content-Type": "application/octet-stream"},
        ) as response:
            output = await response.json()
            return output["cid"]
