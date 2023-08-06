import asyncio
import sys

import docker
from termcolor import colored

from ..client import get_client
from ..cores.ipfs import status_ipfs


def getEnvText(name):
    return colored("[ {} ]".format(name), "green", attrs=["reverse"])


def getFailText():
    return colored("[ FAIL ]", "red", attrs=["reverse"])


def getSuccessText():
    return colored("[ OK ]", "green", attrs=["reverse"])


async def test_run(cf):
    # escrowAccount = await getEscrow(cf, 288, 0)
    # print(escrowAccount)
    # testoutput = "QmT7ynzTEFK8DVEM48RfVo4Rumy4qyMi9Y9doh3doDyJbZ"
    # await descrow(cf, 288, 0, testoutput)
    # a = await test_pda(cf)
    # print(a)
    pass


# returns output


def cmd_status(args, config):
    print("Version " + sys.version)
    print("Version Info " + str(sys.version_info))
    text = ""
    # docker connection
    try:
        docker.DockerClient(base_url=config["system"]["docker_url"])
        text = getSuccessText()
    except:
        text = getFailText()
    print("Docker " + text)
    # daemon connection
    host = config["system"]["xml_rpc_addr"]
    port = config["system"]["xml_rpc_port"]
    c = get_client(host, port)
    if c is None or c.isAlive() is not True:
        text = getFailText()
    else:
        text = getSuccessText()
    print("Daemon " + text)

    ipfs = status_ipfs(
        config["system"]["ipfs_get_gateway"]
        + "/"
        + config["system"]["ipfs_test_hash"]
    )
    if ipfs:
        text = getSuccessText()
    else:
        text = getFailText()
    print("IPFS " + text)

    if c:
        models = c.get_contracts_list()
        print("models")
        print(models)

    asyncio.run(test_run(config))
