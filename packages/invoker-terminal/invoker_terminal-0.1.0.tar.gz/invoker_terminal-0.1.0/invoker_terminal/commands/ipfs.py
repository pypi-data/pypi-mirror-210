from ..storage.deployed_models import checkInference
from ..storage.helper import get_engine


def cmd_ipfs(args, conf):
    print("args ")
    print(args)
    print("conf")
    print(conf)
    engine = get_engine(args.db_path)
    # res = addInference(engine, "local", 1, 1)
    # print(res)
    res2 = checkInference(engine, "local", 1, 2)
    print(res2)
