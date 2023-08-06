import asyncio
import atexit
import json
import os
import sys
import threading
import time
import traceback
import uuid
from multiprocessing import current_process
from pathlib import Path
from struct import pack_into
from time import sleep
from xmlrpc.server import (
    SimpleXMLRPCDispatcher,
    SimpleXMLRPCRequestHandler,
    SimpleXMLRPCServer,
)

import aiodocker
import aiohttp
import websockets
from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey
from solana.rpc.websocket_api import SolanaWsClientProtocol, connect
from solders.pubkey import Pubkey
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID

from .constants import InvokerEnvironment
from .cores.anchor import descrow, getEscrow, getModel
from .cores.ipfs import async_get_from_ipfs, async_send_to_ipfs
from .cores.wallet import getPubkey, loadwallet
from .storage.deployed_models import (
    DeployedModel,
    checkInference,
    getDeployedModels,
    getImageIdByModel,
)
from .storage.helper import get_engine
from .utils import getTaskId

idl = open(
    os.path.dirname(__file__) + "/idl/invoker_network_market.json"
).read()
idl = json.loads(idl)


def exit_handler():
    print("Daemon quitting..do some cleanup")


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)


# Create server
# server = SimpleXMLRPCServer(("localhost", 10001),
#                            requestHandler=RequestHandler)
# server.register_introspection_functions()

# Register pow() function; this will use the value of
# pow.__name__ as the name, which is just 'pow'.

import logging
from logging.handlers import RotatingFileHandler

logger = None

quitFlag = 0


def quit():
    global quitFlag
    quitFlag = 1
    logger.info("quiting....")
    return 1


def isAlive():
    return True


tasks_listening = {}


async def docker_run(cf, input: bytes, image_id: str) -> bytes:
    logger = logging.getLogger("DockerExecutor")
    id = uuid.uuid4()
    host_url = os.path.join(cf["system"]["tmp_folder"], str(id))
    Path(host_url).mkdir(parents=True, exist_ok=True)
    logger.info("Host url {}".format(host_url))
    with open("{}/input.zip".format(host_url), "wb") as f:
        f.write(input)

    docker = aiodocker.Docker(cf["system"]["docker_url"])
    container_config = {
        "Image": "{}".format(image_id),
        "HostConfig": {"Binds": [f"{host_url}:/invoker"]},
    }
    logger.info("Container ID {}".format(str(id)))
    logger.info("Container Config {}".format(container_config))
    container = await docker.containers.create_or_replace(
        str(id), container_config
    )
    await container.start()
    await container.wait()
    await container.delete(force=True)
    await docker.close()
    output = open("{}/output.zip".format(host_url), "rb").read()
    # todo
    # delete host mount point here
    return output


async def heart_beat(cf, model: DeployedModel):
    HEARTBEAT_INTERVAL = 15
    logger = logging.getLogger("HeartBeat")
    keystr = cf["system"]["wallet"]
    keypair = loadwallet(keystr)
    sk = SigningKey(keypair.secret())
    url = cf["system"]["heart_beat_url"]
    modelId = model.model_id
    env = model.env

    while quitFlag != 1:
        status = tasks_listening.get("{}_{}".format(env, modelId), False)
        if env == "local" or env == "dev":
            logger.info("Heartbeat is disabled for local and dev environments")
            status = False

        if status:
            logger.info(
                "pumping every {} sec for {} - [status] {}".format(
                    HEARTBEAT_INTERVAL, modelId, status
                )
            )
            msg = {}
            msg["ts"] = time.time()
            msg["pk"] = str(keypair.pubkey())
            msg["modelid"] = modelId
            msg["content"] = "hb"
            jsonstr = json.dumps(msg)
            signed = sk.sign(jsonstr.encode("utf-8"), encoder=Base64Encoder)
            postpayload = {}
            postpayload["modelid"] = modelId
            postpayload["pk"] = str(keypair.pubkey())
            postpayload["sig"] = str(signed)
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(url, json=postpayload) as resp:
                        # print(resp.status)
                        # print(await resp.text())
                        logger.info("OK - {}".format(modelId))
                except Exception as e:
                    logger.error("FAIL - {}".format(modelId))
                    logger.error(e)
                finally:
                    await session.close()

        await asyncio.sleep(HEARTBEAT_INTERVAL)
    logger.info("is quiting...")


async def invoke_executor(args, cf, loop, engine, env, modelid, inferenceid):
    logger = logging.getLogger(
        "InvokeExecutor for {} {} {}".format(env, modelid, inferenceid)
    )
    try:
        escrowAccount = await getEscrow(cf, modelid, inferenceid)
        ipfsfile = await async_get_from_ipfs(
            loop, escrowAccount.input, cf["system"]["ipfs_get_gateway"]
        )
        imageid = getImageIdByModel(engine, env, modelid)
        logger.info("Fetch image id {}".format(imageid))
        output = await docker_run(cf, ipfsfile, imageid)
        ipfsoutput = await async_send_to_ipfs(
            loop, output, cf["system"]["ipfs_post_gateway"]
        )
        logger.info("Output hash {}".format(ipfsoutput))
        await descrow(cf, modelid, inferenceid, ipfsoutput)
    except:
        logger.info("{} {} {} failed".format(env, modelid, inferenceid))


async def invoke_processor(args, cf, invokeQ: asyncio.Queue):
    logger = logging.getLogger("Invoke Processor")
    logger.info("starting...")
    engine = get_engine(args.db_path)
    while quitFlag != 1:
        (env, modelid, inferenceid) = await invokeQ.get()
        loop = asyncio.get_event_loop()
        loop.create_task(
            invoke_executor(args, cf, loop, engine, env, modelid, inferenceid)
        )
    # parse the inputs
    # execute in docker
    # if everything is okay
    # descrow
    # if evrything is okay
    # mark the database as task is done.
    logger.info("done...")
    pass


async def notify_processor(
    args, config, engine, notifyQ: asyncio.Queue, invokeQ: asyncio.Queue
):
    logger = logging.getLogger("Notify Processor")
    try:
        while quitFlag != 1:
            logger.info("waiting for processing...")
            (env, modelid) = await notifyQ.get()
            model = await getModel(config, modelid)
            last_inference = model.inference_count - 1
            if not checkInference(engine, env, modelid, last_inference):
                # invokeQ()
                logger.info(
                    "inference not found {} {} {}".format(
                        env, modelid, last_inference
                    )
                )
                await invokeQ.put((env, modelid, last_inference))
                pass
            # get account info for the model
            # get latest inference
            # check if it is in our storage marked as success.
            # if not send to the invoke que
            logger.info(
                "item {} on {} has been processed".format(env, modelid)
            )
    except EOFError:
        logger.info("Connection closed brutally")
    logger.info("is quitting...")


tasks = {}


async def listen_account_change(cf, notifyQ, model: DeployedModel):
    logger = logging.getLogger("Connection")
    env = model.env
    wss = cf[env]["websocket_url"]
    buffer = bytearray(16)
    modelId = model.model_id
    pack_into("<I", buffer, 0, modelId)
    modelAddr, _ = Pubkey.find_program_address(
        seeds=[bytes(buffer), bytes("model", "utf-8")],
        program_id=getPubkey(idl["metadata"]["address"]),
    )
    logger.info(
        "starting to listening model account changes for {} on {}".format(
            modelId, env
        )
    )
    subscription_id = None
    try:
        async with connect(wss) as websocket:
            await websocket.account_subscribe(modelAddr, encoding="base64")
            logger.info("I subscribe websocket")
            first_resp = await websocket.recv()
            # print(first_resp)
            logger.info("first resp")
            logger.info(first_resp)
            subscription_id = first_resp[0].id
            # subscription_id = first_resp.result
            tasks_listening["{}_{}".format(env, modelId)] = True
            async for msg in websocket:
                logger.info(
                    "Account has been changed for {} {}".format(env, modelId)
                )
                await notifyQ.put((env, modelId))
    except websockets.exceptions.ConnectionClosedError:
        logger.info("Connection closed... But trying to reconnect again")
        await asyncio.sleep(3)
        pass
    except asyncio.exceptions.IncompleteReadError:
        logger.info("Incomplete read error...***")
        await asyncio.sleep(3)
        pass
    except OSError:
        logger.info("Os Error here but keep moving")
        await asyncio.sleep(3)
        pass
    finally:
        tasks_listening["{}_{}".format(env, modelId)] = False
        tb = traceback.format_exc()
        logger.info(tb)
        try:
            logger.info("trying to unsub here for {}".format(subscription_id))
            if subscription_id:
                logger.info("really unsubbing here")
                # await websocket.logs_unsubscribe(subscription_id)
        except asyncio.exceptions.IncompleteReadError:
            logger.info("it is fine keep going")
            pass


def get_contracts_list():
    dummy = {}
    for key in tasks_listening.keys():
        dummy[str(key)] = tasks_listening[key]
    return dummy


async def start_account_listener(cf, notifyQ, model: DeployedModel):
    task_id = getTaskId(model)
    logger = logging.getLogger("Connection")
    while True:
        if quitFlag == 1:
            break

        if task_id in tasks and not tasks[task_id].done():
            logger.info(f"Task {task_id} is already running")
        else:
            # Create a new event loop for the task
            loop = asyncio.get_running_loop()

            # Start a new task on the new event loop
            tasks[task_id] = loop.create_task(
                listen_account_change(cf, notifyQ, model)
            )
            logger.info(f"Started new task {task_id}")

        # Wait for the task to complete before running it again
        await tasks[task_id]


async def kill_switch(cf):
    logger = logging.getLogger("Daemon")
    while True:
        if quitFlag == 1:
            loop = asyncio.get_event_loop()
            loop.stop()
            break
        logger.info("kill switch quit flag {}".format(quitFlag))
        await asyncio.sleep(5)


async def start_tasks(args, cf):
    notifyQ = asyncio.Queue()
    invokeQ = asyncio.Queue()
    engine = get_engine(args.db_path)
    models = getDeployedModels(engine)
    tasklist = [
        kill_switch(cf),
        notify_processor(args, cf, engine, notifyQ, invokeQ),
        invoke_processor(args, cf, invokeQ),
    ]
    for model in models:
        tasklist.append(start_account_listener(cf, notifyQ, model))
        tasklist.append(heart_beat(cf, model))
    await asyncio.gather(*tasklist)


def account_listener(args, cf):
    logger = logging.getLogger("Connection")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(start_tasks(args, cf))
    except RuntimeError:
        logger.info("Runtime error received from asyncio loop")
        pass
    logger.info("account listener is quitting...")


# function to be executed in a new process
def task(argz, config):
    global quitFlag
    global logger
    ###
    logrotate = RotatingFileHandler(
        filename=argz.log_path,
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=1,
        encoding=None,
        delay=0,
    )

    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=int(config["system"]["log_level"]),
        handlers=[logrotate],
    )
    logger = logging.getLogger("Daemon")

    logging.info("from daemon {}".format(argz))
    logging.info("from daemon {}".format(config))
    # get the current process
    process = current_process()
    atexit.register(exit_handler)
    # report if daemon process
    logging.info(f"Daemon process: {process.daemon}")
    host = config["system"]["xml_rpc_addr"]
    port = config["system"]["xml_rpc_port"]
    server = SimpleXMLRPCServer(
        (host, int(port)), requestHandler=RequestHandler
    )
    server.register_function(pow)
    server.register_function(quit)
    server.register_function(isAlive)
    server.register_function(get_contracts_list)

    threads = []
    threads.append(
        threading.Thread(target=account_listener, args=(argz, config))
    )

    for t in threads:
        t.start()

    while quitFlag != 1:
        server.handle_request()

    loop = asyncio.get_event_loop()
    loop.close()

    for t in threads:
        t.join()
