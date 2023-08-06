from solders.keypair import Keypair
from solders.pubkey import Pubkey


def generatewallet() -> Keypair:
    return Keypair()


def loadwallet(js) -> Keypair:
    kp = Keypair.from_json(js)
    return kp


def getPubkey(pk: str) -> Pubkey:
    return Pubkey.from_string(pk)
