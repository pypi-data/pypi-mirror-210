import json
import os
from struct import pack, pack_into
from typing import Tuple

from anchorpy import Context, Idl, Program, Provider, Wallet
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from spl.token.client import Token
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID
from spl.token.core import AccountInfo
from spl.token.instructions import get_associated_token_address

from ..utils import generateModelUrl
from .wallet import getPubkey, loadwallet

max_int64 = 0xFFFFFFFFFFFFFFFF


class InvokerModel:
    owner: Pubkey
    description: str
    price: int
    token_mint: Pubkey
    inference_count: int


class EscrowAccount:
    requester: Pubkey
    input: str
    output: str


rawidl = open(
    os.path.dirname(__file__) + "/../idl/invoker_network_market.json"
).read()
# rawidl = json.load(rawidl)
idlparsed = json.loads(rawidl)


def getMarketSettingsPDA() -> Tuple[Pubkey, int]:
    marketSettingsPDA, marketSettingsBump = Pubkey.find_program_address(
        seeds=[bytes("market-settings", "utf-8")],
        program_id=getPubkey(idlparsed["metadata"]["address"]),
    )

    return marketSettingsPDA, marketSettingsBump


def getEscrowWalletPDA(modelId: int, inferenceid: int) -> Pubkey:
    # inferencebuffer = bytearray(16)
    # modelbuffer = bytearray(16)
    # pack_into("<I", modelbuffer, 0, modelId)
    # pack_into("<I", inferencebuffer, 0, inferenceid)
    inferencebuffer = pack(
        "<QQ", inferenceid & max_int64, (inferenceid >> 64) & max_int64
    )
    modelbuffer = pack("<QQ", modelId & max_int64, (modelId >> 64) & max_int64)

    escrowWalletPDA, _ = Pubkey.find_program_address(
        seeds=[
            bytes(inferencebuffer),
            bytes(modelbuffer),
            bytes("escrow-wallet", "utf-8"),
        ],
        program_id=getPubkey(idlparsed["metadata"]["address"]),
    )
    return escrowWalletPDA


def getEscrowAccountPDA(modelId: int, inferenceid: int) -> Pubkey:
    # inferencebuffer = bytearray(16)
    # modelbuffer = bytearray(16)
    # pack_into("<I", modelbuffer, 0, modelId)
    # pack_into("<I", inferencebuffer, 0, inferenceid)
    inferencebuffer = pack(
        "<QQ", inferenceid & max_int64, (inferenceid >> 64) & max_int64
    )
    modelbuffer = pack("<QQ", modelId & max_int64, (modelId >> 64) & max_int64)

    escrowPDA, _ = Pubkey.find_program_address(
        seeds=[
            bytes(inferencebuffer),
            bytes(modelbuffer),
            bytes("escrow", "utf-8"),
        ],
        program_id=getPubkey(idlparsed["metadata"]["address"]),
    )
    return escrowPDA


def getModelPDA(modelId: int) -> Pubkey:
    max_int64 = 0xFFFFFFFFFFFFFFFF
    packed = pack("<QQ", modelId & max_int64, (modelId >> 64) & max_int64)
    modelPDA, _ = Pubkey.find_program_address(
        seeds=[bytes(packed), bytes("model", "utf-8")],
        program_id=getPubkey(idlparsed["metadata"]["address"]),
    )
    return modelPDA


def getWallet(config):
    keystr = config["system"]["wallet"]
    keypair = loadwallet(keystr)
    return Wallet(keypair)


def getKeypair(config):
    keystr = config["system"]["wallet"]
    keypair = loadwallet(keystr)
    return keypair


def getProgram(config) -> Program:
    wallet = getWallet(config)
    client = AsyncClient(config["active"]["rpc_url"])
    provider = Provider(client, wallet)
    program_id = getPubkey(idlparsed["metadata"]["address"])
    idlAnchor = Idl.from_json(rawidl)
    return Program(idlAnchor, program_id, provider)


async def getEscrow(config, modelId: int, inferenceId: int) -> EscrowAccount:
    async with getProgram(config) as program:
        escrowPDA = getEscrowAccountPDA(modelId, inferenceId)
        escrowAccount = await program.account["EscrowAccount"].fetch(escrowPDA)
        return escrowAccount


async def getModel(config, modelId: int) -> InvokerModel:
    async with getProgram(config) as program:
        modelPDA = getModelPDA(modelId)
        modelAccount = await program.account["InvokerModel"].fetch(modelPDA)
        return modelAccount


def get_or_create_token_account(
    client: Client, owner: Pubkey, tokenmint: Pubkey, payer: Keypair
) -> AccountInfo:
    addr = get_associated_token_address(owner, tokenmint)
    token = Token(client, tokenmint, TOKEN_PROGRAM_ID, payer)
    try:
        return token.get_account_info(addr)
    except Exception as e:
        token.create_associated_token_account(owner)
        return get_or_create_token_account(client, owner, tokenmint, payer)


async def test_pda(config):
    async with getProgram(config) as program:
        pk = Pubkey.from_string("F48tYLEGkyjt4PU5AFbe43fJcaQmG5AUh79GMBvFhUD1")
        escrowAccount = await program.account["EscrowAccount"].fetch(pk)
        return escrowAccount


async def descrow(config, modelid: int, inferenceid: int, output: str):
    wallet = getWallet(config)
    async with getProgram(config) as program:
        marketSettingsPDA, marketSettingsBump = getMarketSettingsPDA()
        marketSettings = await program.account["MarketSettings"].fetch(
            marketSettingsPDA
        )
        modelPDA = getModelPDA(modelid)
        model = await getModel(config, modelid)
        escrowAccountPDA = getEscrowAccountPDA(modelid, inferenceid)
        escrowWalletPDA = getEscrowWalletPDA(modelid, inferenceid)
        invokerTokenAccount = get_associated_token_address(
            wallet.public_key, model.token_mint
        )
        ownerTokenAccount = get_associated_token_address(
            marketSettings.owner, model.token_mint
        )
        accounts = {
            "invoker": wallet.public_key,
            "mint_of_token_being_sent": model.token_mint,
            "invoker_taker_token_account": invokerTokenAccount,
            "owner_token_account": ownerTokenAccount,
            "market_settings": marketSettingsPDA,
            "market_owner": marketSettings.owner,
            "model": modelPDA,
            "escrow_account": escrowAccountPDA,
            "escrow_wallet": escrowWalletPDA,
            "system_program": SYS_PROGRAM_ID,
            "token_program": TOKEN_PROGRAM_ID,
        }
        await program.rpc["descrow"](
            modelid,
            inferenceid,
            output,
            ctx=Context(accounts=accounts, signers=[getKeypair(config)]),
        )


async def addModel(
    config, modelDescription: str, tokenMint: Pubkey, price: int
) -> int:
    wallet = getWallet(config)
    keypair = getKeypair(config)
    print("preparing deployment...")
    async with getProgram(config) as program:
        marketSettingsPDA, marketSettingsBump = getMarketSettingsPDA()
        marketSettings = await program.account["MarketSettings"].fetch(
            marketSettingsPDA
        )
        modelPDA = getModelPDA(marketSettings.model_id)
        accounts = {
            "market_owner": marketSettings.owner,
            "market_settings": marketSettingsPDA,
            "model": modelPDA,
            "user": keypair.pubkey(),
            "system_program": SYS_PROGRAM_ID,
        }
        res = await program.rpc["addmodel"](
            marketSettingsBump,
            modelDescription,
            price,
            tokenMint,
            ctx=Context(accounts=accounts, signers=[keypair]),
        )
        print("Transaction has been sent")
        return marketSettings.model_id
