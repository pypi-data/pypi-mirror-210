import io
import json
import os
import shutil
import uuid
import zipfile
from pathlib import Path

import docker

from ..cores.invoker_init import ParseInput
from ..cores.wallet import generatewallet


def cmd_test(args, config):
    id = uuid.uuid4()
    host_url = os.path.join(config["system"]["tmp_folder"], str(id))
    print(host_url)
    Path(host_url).mkdir(parents=True, exist_ok=True)
    print(os.listdir(host_url))

    dummyinput = """
    {
    "description": "My own description",
    "inputs": [
        {
            "description": "count variable used in the model",
            "maxNum": 1000,
            "minNum": 100,
            "name": "count",
            "slider": false,
            "type": "number",
            "value": 500
        },
        {
            "description": "my description here",
            "maxchar": 200,
            "minchar": 10,
            "name": "prompt",
            "textarea": false,
            "type": "text",
            "value": "a generous prompt is here"
        },
        {
            "description": "",
            "maxchar": -1,
            "minchar": -1,
            "name": "prompt2",
            "textarea": false,
            "type": "text",
            "value": "a new version of promppt2 is here"
        }
    ],
    "name": "Facebook llama model"
}

"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(
        zip_buffer, "a", zipfile.ZIP_DEFLATED, False
    ) as zip_file:
        for file_name, data in [
            ("input.json", io.BytesIO(dummyinput.encode("utf-8"))),
            ("2.txt", io.BytesIO(b"222")),
        ]:
            zip_file.writestr(file_name, data.getvalue())

    with open("{}/input.zip".format(host_url), "wb") as f:
        f.write(zip_buffer.getvalue())

    client = docker.DockerClient(base_url=config["system"]["docker_url"])
    volumes = [host_url]
    volume_bindings = {
        "{}".format(host_url): {
            "bind": "/invoker",
            "mode": "rw",
        },
    }

    host_config = client.api.create_host_config(binds=volume_bindings)

    f = json.load(open("./build.json"))
    print("id is {}".format(f["id"]))
    container = client.api.create_container(
        f["id"], volumes=volumes, host_config=host_config
    )
    response = client.api.start(container=container.get("Id"))
    logs = client.api.logs(container=container.get("Id"))
    print("--logs--")
    print(logs)
    print(response)
    # container = client.containers.run(f['id'],volumes=volumes, host_config=host_config)
    print(container)
    print(type(container))
    # print(container.logs())

    print(os.listdir(host_url))

    wallet = generatewallet()
    print(wallet)
    print(wallet.to_json())
    # delete the temp folder
    try:
        # shutil.rmtree(host_url)
        # print("DELETE - OK")
        pass
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
