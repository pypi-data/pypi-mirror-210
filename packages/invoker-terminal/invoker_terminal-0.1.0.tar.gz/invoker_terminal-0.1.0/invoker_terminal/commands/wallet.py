import logging
from typing import get_args

from solana.rpc.api import Client
from solders.rpc.responses import RPCError, RPCResult

from ..constants import (
    dev_test_token_addr,
    mainnet_tether_addr,
    mainnet_usdc_addr,
)
from ..cores.anchor import get_or_create_token_account
from ..cores.wallet import getPubkey, loadwallet

AIRDROP_AMOUNT = 10_000_000_000

RPC_RESULT_TYPES = get_args(RPCResult)


def assert_valid_response(resp: RPCResult):
    """Assert valid RPCResult."""
    assert type(resp) in RPC_RESULT_TYPES
    assert not isinstance(resp, RPCError.__args__)  # type: ignore


def cmd_wallet(args, config):
    logging.info("Wallet is loading...")
    keystr = config["system"]["wallet"]
    keypair = loadwallet(keystr)
    pubkey = keypair.pubkey()
    dev_client = Client(config["active"]["rpc_url"])
    main_client = Client(config["active"]["rpc_url"])
    tx = None
    try:
        # tx = dev_client.request_airdrop(pubkey, 1000000000, "finalized")
        # assert_valid_response(tx)
        # dev_client.confirm_transaction(tx.value)
        pass
    except:
        pass
    print("Wallet: {}".format(pubkey))

    # dev stats
    dev_balance = dev_client.get_balance(pubkey)
    print("Dev Balance: {}".format(dev_balance.value))
    dev_test_token_pub = getPubkey(dev_test_token_addr)
    dev_tether_balance = get_or_create_token_account(
        dev_client, pubkey, dev_test_token_pub, keypair
    )
    print("Dev Tether Balance: {}".format(dev_tether_balance.amount))

    """
    mainnet_balance = main_client.get_balance(pubkey).value
    print("*Mainnet Balance: {}".format(mainnet_balance))
    if mainnet_balance == 0:
        print("You need to deposit some coins to do mainnet operations. Please refer to our documentation. https://docs.invoker.network")
    else:
        mainnet_tether_token_pub = getPubkey(mainnet_tether_addr)
        mainnet_tether_balance = get_or_create_token_account(main_client, pubkey, mainnet_tether_token_pub, keypair)
        print("*Mainnet Tether Balance: {}".format(mainnet_tether_balance.amount))
    """

    # print(dev_tether_token.get_accounts_by_owner_json_parsed(pubkey))
    # print(dev_tether_token.get_accounts_by_owner_json_parsed(getPubkey("4YYKD5WMmQYyMXX7i7KpFfKHiDmKvpo16PtFVrcBiERE")))
    # print(dev_tether_token.get_mint_info())
    # addr = get_associated_token_address(getPubkey("4YYKD5WMmQYyMXX7i7KpFfKHiDmKvpo16PtFVrcBiERE"), dev_tether_pub)
    # print(dev_tether_token.get_account_info(addr))
    # print(dev_tether_token.get_balance(addr))

    # addr = get_associated_token_address(pubkey, dev_tether_pub)
    # print(addr)
    # print(dev_tether_token.get_account_info(addr))
    # print(dev_tether_token.get_balance(addr))

    # print(dev_tether_token.get_account_info(getPubkey("4YYKD5WMmQYyMXX7i7KpFfKHiDmKvpo16PtFVrcBiERE")))
    # print(dev_tether_token.get_balance(getPubkey("4YYKD5WMmQYyMXX7i7KpFfKHiDmKvpo16PtFVrcBiERE")))
    # print(dev_tether_token)
    # dev_tether_balance = dev_client.get_token_account_balance(dev_tether_pub)
    # print("Dev Tether Balance: {}".format(dev_tether_balance))
    # dev_usdc_pub = getPubkey(dev_usdc)
    # dev_usdc_balance = dev_client.get_token_account_balance(dev_usdc_pub)
    # print("Dev USDC Balance: {}".format(dev_usdc_balance))

    # mainnet stats
    # mainnet_balance = main_client.get_balance(pubkey)
    # print("Mainnet Balance: {}".format(mainnet_balance.value))
    # mainnet_tether_token = Token()
    # mainnet_tether_pub = getPubkey(main_tether)
    # mainnet_tether_token = Token(main_client, mainnet_tether_pub, TOKEN_PROGRAM_ID, keypair)
    # acc = mainnet_tether_token.get_accounts_by_owner(pubkey)
    # acc = mainnet_tether_token.get_account_info(keypair.pubkey())
    # print(acc)
    # acc = mainnet_tether_token.create_account(pubkey)
    # mainnet_tether_token.get_account_info
    # mainnet_tether_account = mainnet_tether_token.get_balance(acc)
    # print("Mainnet Tether Balance: {}".format(mainnet_tether_account.value.amount))
    # Token.create_account(mainnet_tether_token, pubkey)

    # print(mainnet_tether_pub)
    # opts = TokenAccountOpts(mint=mainnet_tether_pub)
    # mainnet_tether_account = main_client.get_token_accounts_by_owner_json_parsed(pubkey, opts, 'finalized')
    # test = main_client.get_token_account_balance(mainnet_tether_pub)
    # print(mainnet_tether_account)
    # print(test)
    # mainnet_tether_balance = main_client.get_token_account_balance(mainnet_tether_account)
    # print("Mainnet Tether Balance: {}".format(mainnet_tether_balance))
    # mainnet_usdc_pub = getPubkey(main_usdc)
    # mainnet_usdc_balance = main_client.get_token_account_balance(mainnet_usdc_pub)
    # print("Mainnet USDC Balance: {}".format(mainnet_usdc_balance))
