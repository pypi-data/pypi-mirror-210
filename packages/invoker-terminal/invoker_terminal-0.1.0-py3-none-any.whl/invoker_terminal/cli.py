"""CLI interface for invoker_terminal project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""
import argparse
import configparser
import logging
import os
from argparse import RawTextHelpFormatter
from logging.handlers import RotatingFileHandler

from .commands.build import cmd_build
from .commands.daemon import cmd_daemon
from .commands.deploy import cmd_deploy
from .commands.history import cmd_history
from .commands.init import cmd_init
from .commands.invoke import cmd_invoke
from .commands.ipfs import cmd_ipfs
from .commands.new_task import cmd_new_task
from .commands.status import cmd_status, getEnvText
from .commands.test import cmd_test
from .commands.wallet import cmd_wallet
from .storage.helper import get_engine, init_tables

commandMap = {
    "init": cmd_init,
    "status": cmd_status,
    "daemon": cmd_daemon,
    "wallet": cmd_wallet,
    "new": cmd_new_task,
    "invoke": cmd_invoke,
    "build": cmd_build,
    "test": cmd_test,
    "deploy": cmd_deploy,
    "history": cmd_history,
    "ipfs": cmd_ipfs,
}

PROGRAM_NAME = "invoker_terminal"


def main():
    version = open(os.path.dirname(__file__) + "/VERSION").read()
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description="""
        A terminal that connects to Invoker Network (https://invoker.network)
        """,
        formatter_class=RawTextHelpFormatter,
        epilog="""
    init: initialize a config and cache
    status: status information about daemon and dependencies
    daemon: start/stop daemon a.k.a the background process
    wallet: information about wallet & tokens
    new: generates a boilerplate for AI task
    build: builds the task
    invoke: invoke the  model (inside container)
    test: tests the task
    deploy: deploys the task
    history: shows recent transactions

    Version: {version}
    """.format(
            version=version
        ),
    )

    invo_config_dir = os.path.expanduser("~") + os.sep + ".invokernet"
    invo_config = invo_config_dir + os.sep + "config.ini"
    db_path = invo_config_dir + os.sep + "invoker.db"
    log_path = invo_config_dir + os.sep + "system.log"

    config = configparser.ConfigParser()

    parser.add_argument(
        "command", nargs=1, choices=commandMap.keys(), default="status"
    )
    parser.add_argument(
        "--debug", action="store_true", help="enable debug environment"
    )
    parser.add_argument("--conf", action="append", default=[invo_config])

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--local",
        dest="env",
        action="store_const",
        const="l",
        help="local environment",
    )
    group.add_argument(
        "--dev",
        dest="env",
        action="store_const",
        const="d",
        help="dev environment",
    )
    group.add_argument(
        "--main",
        dest="env",
        action="store_const",
        const="m",
        help="prod environment",
    )
    parser.set_defaults(env="l", db_path=db_path, log_path=log_path)
    args = parser.parse_args()

    print("Config loaded from {}".format(args.conf))

    if args.conf is not None:
        for conf_fname in args.conf:
            if not os.path.isfile(conf_fname):
                logging.debug("Skipping {}. Not found!".format(conf_fname))
            else:
                logging.info("loading config from {}".format(conf_fname))
                config.read(conf_fname)

    logrotate = RotatingFileHandler(
        filename=log_path,
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

    engine = get_engine(db_path)
    init_tables(engine)
    logging.info("Invoker DB loaded from {}".format(db_path))

    config.add_section("active")
    if args.env == "l":
        print("Environment " + getEnvText("LOCAL"))
        config["active"]["rpc_url"] = config["local"]["rpc_url"]
        config["active"]["websocket_url"] = config["local"]["websocket_url"]

    if args.env == "d":
        print("Environment " + getEnvText("DEV"))
        config["active"]["rpc_url"] = config["dev"]["rpc_url"]
        config["active"]["websocket_url"] = config["dev"]["websocket_url"]

    if args.env == "m":
        print("Environment " + getEnvText("MAINNET"))
        config["active"]["rpc_url"] = config["mainnet"]["rpc_url"]
        config["active"]["websocket_url"] = config["mainnet"]["websocket_url"]

    # print(config.has_section('system'))
    if args.command != ["init"]:
        if not config.has_section("system"):
            parser.error(
                """

            needs a valid config before running

            type "{PROGRAM_NAME} init" to generate config

            """.format(
                    PROGRAM_NAME=PROGRAM_NAME
                )
            )

    # if args.command != ['deploy'] and args.prod:
    #    parser.error('--prod can only be set when deploy.')

    # if args.command == ['deploy'] and args.prod:
    #    if not config.has_section('prod'):
    #        parser.error('config needs to have --prod section')

    command = args.command[0]
    commandMap[command](args, config)
