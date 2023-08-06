import logging
import os

DOCKERFILE_FILE = (
    os.path.dirname(__file__) + "/../templates/Dockerfile_template"
)
MODEL_FILE = os.path.dirname(__file__) + "/../templates/model.py"

model_template = open(MODEL_FILE).read()
dockerfile_template = open(DOCKERFILE_FILE).read()


def cmd_new_task(args, config):
    cwd = os.getcwd()
    name = str(input("Enter model name: "))
    print(name)
    print(cwd)
    if os.path.isdir(name):
        logging.info("Directory exists {name}".format(name=name))
        os._exit(1)
    elif not os.access(cwd, os.W_OK):
        logging.info("Directory is not writable... {dir}".format(dir=cwd))
        os._exit(1)
    else:
        logging.info("Creating task files...")
        newpath = cwd + "/" + name
        os.makedirs(newpath, exist_ok=False)

        # dockerfile
        f = open(newpath + "/Dockerfile", "w+")
        f.write(dockerfile_template)
        f.close()

        # modelpy
        f = open(newpath + "/model.py", "w")
        f.write(model_template)
        f.close()

    # name = input('What is the task name? (must be unique)\n')
    # print(name)
