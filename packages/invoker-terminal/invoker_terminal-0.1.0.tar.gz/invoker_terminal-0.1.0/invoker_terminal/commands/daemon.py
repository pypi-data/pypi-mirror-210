import logging
import os
from multiprocessing import Process
from time import sleep

from ..client import get_client
from ..server import task


def init_daemon(args, config):
    if os.fork() != 0:
        return
    process = Process(target=task, args=(args, config), daemon=True)
    # start the new process
    process.start()
    process.join()


def cmd_daemon(args, config):
    logging.info("Im the daemon")
    host = config["system"]["xml_rpc_addr"]
    port = config["system"]["xml_rpc_port"]
    c = get_client(host, port)
    if c is not None and c.isAlive() is True:
        logging.info("shutting down")
        c.quit()
    else:
        logging.info("spawning the daemon")
        init_daemon(args, config)
        sleep(2)
