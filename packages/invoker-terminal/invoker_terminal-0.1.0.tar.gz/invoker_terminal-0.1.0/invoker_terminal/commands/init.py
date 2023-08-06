import logging
import os

from ..cores.wallet import generatewallet

heart_beat_url = "https://hb.invoker.network/app"

ipfs_post_gateway = "https://ipfs.invoker.network/app/ipfs-route"
ipfs_get_gateway = "https://ipfs.invoker.network/gateway/ipfs/"
ipfs_test_hash = "QmdUUfATjEKuhNQacktJJWUydfz7Zh3xfwKAkRfXU7eNB9"

docker_url = "unix:///var/run/docker.sock"
docker_sock = "tcp://127.0.0.1:1234"
xml_rpc_addr = "localhost"
xml_rpc_port = 9005
tmp_folder = "/tmp/"

local_rpc_url = "http://127.0.0.1:8899"
local_websocket_url = "ws://localhost:8900"

dev_rpc_url = "https://api.devnet.solana.com"
dev_websocket_url = "wss://multi-proportionate-firefly.solana-devnet.discover.quiknode.pro/8149116fe82f66981c679c6b701e03a67fb1cb68/"

mainnet_rpc_url = "https://api.devnet.solana.com"
mainnet_websocket_url = "wss://multi-proportionate-firefly.solana-devnet.discover.quiknode.pro/8149116fe82f66981c679c6b701e03a67fb1cb68/"


def cmd_init(args, config):
    logging.info("Initializing config...")
    filepath = args.conf[-1]
    if os.path.isfile(filepath):
        logging.info("Config file exists. I can't overwrite it")
        os._exit(-1)
    else:
        p = os.path.dirname(os.path.abspath(filepath))
        logging.info("Directory is {}".format(p))
        os.makedirs(p, exist_ok=True)
    config["system"] = {}
    config["system"]["heart_beat_url"] = str(heart_beat_url)
    config["system"]["ipfs_post_gateway"] = str(ipfs_post_gateway)
    config["system"]["ipfs_get_gateway"] = str(ipfs_get_gateway)
    config["system"]["ipfs_test_hash"] = str(ipfs_test_hash)
    config["system"]["docker_url"] = str(docker_url)
    config["system"]["docker_sock"] = str(docker_sock)
    config["system"]["xml_rpc_addr"] = str(xml_rpc_addr)
    config["system"]["xml_rpc_port"] = str(xml_rpc_port)
    config["system"]["tmp_folder"] = str(tmp_folder)
    config["system"]["log_level"] = str(20)
    config["system"]["wallet"] = generatewallet().to_json()
    config["local"] = {}
    config["local"]["rpc_url"] = local_rpc_url
    config["local"]["websocket_url"] = local_websocket_url
    config["dev"] = {}
    config["dev"]["rpc_url"] = dev_rpc_url
    config["dev"]["websocket_url"] = dev_websocket_url
    config["mainnet"] = {}
    config["mainnet"]["rpc_url"] = mainnet_rpc_url
    config["mainnet"]["websocket_url"] = mainnet_websocket_url

    configfile = open(filepath, "w")
    logging.info("saving to file {}".format(filepath))
    config.write(configfile)
