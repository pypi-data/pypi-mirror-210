import json
import logging
import os
import docker
from ..ast_check import model_check


def cmd_build(args, config):
    filesTocCheck = ["Dockerfile", "init.py"]
    client = docker.DockerClient(base_url=config["system"]["docker_url"])
    for f in filesTocCheck:
        if not os.path.isfile(f):
            logging.info("Mising file {file}".format(file=f))
            os._exit(1)
    logging.info("Building...")
    try:
        dockerfile = os.getcwd()
        print(dockerfile)
        (img, logs) = client.images.build(path=dockerfile)
        print(logs)
        for log in logs:
            print(log)
        build = {"id": str(img.id)}
        logging.info("Image ID {}".format(img.id))
        f = open("./build.json", "w")
        f.write(json.dumps(build))
        f.close()

        if not os.path.isfile("./model.py"):
            logging.info("Missing file {file}".format(file="model.py"))
            os._exit(1)

        model_check()

    except Exception as e:
        print("exception here... handle later")
        print(e)
