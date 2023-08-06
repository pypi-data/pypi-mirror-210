from .constants import InvokerEnv, InvokerEnvironment, TokenMap
from .storage.deployed_models import DeployedModel


def getTaskId(m: DeployedModel) -> str:
    return "{}_{}".format(m.env, m.model_id)


def IN_assert(input, output):
    assert input == output


def getEnvName(args) -> InvokerEnvironment:
    if args.env == InvokerEnv.LOCAL:
        return "local"
    if args.env == InvokerEnv.DEV:
        return "dev"
    if args.env == InvokerEnv.MAINNET:
        return "mainnet"
    raise ValueError("Invalid Environment")


def generateModelUrl(args, modelId) -> str:
    if args.env == InvokerEnv.LOCAL:
        return "http://localhost:3000/{}".format(modelId)
    if args.env == InvokerEnv.DEV:
        return "https://dev.invoker.network/{}".format(modelId)
    if args.env == InvokerEnv.MAINNET:
        return "https://invoker.network/{}".format(modelId)
    raise ValueError("Invalid Environment")


def getAvailableTokens(args):
    t = TokenMap.get(args.env, None)
    if t is None:
        raise ValueError("Invalid Environment")
    return t
