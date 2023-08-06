from typing import Literal

local_test_token_addr = "FzZDZZW9r6zg4Qnod6yxrDBkEghBdzmG59pL3SHzWhar"

dev_test_token_addr = "FzZDZZW9r6zg4Qnod6yxrDBkEghBdzmG59pL3SHzWhar"

mainnet_usdc_addr = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
mainnet_tether_addr = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"

InvokerEnvironment = Literal["local", "dev", "mainnet"]


class InvokerEnv:
    LOCAL = "l"
    DEV = "d"
    MAINNET = "m"


TokenMap = {
    InvokerEnv.LOCAL: [
        {
            "TokenName": "InvokerLocalTestToken",
            "Address": local_test_token_addr,
        },
    ],
    InvokerEnv.DEV: [
        {"TokenName": "InvokerDevToken", "Address": dev_test_token_addr}
    ],
    InvokerEnv.MAINNET: [
        {"TokenName": "USDC (Circle)", "Address": mainnet_usdc_addr},
        {"TokenName": "USDT (Tether)", "Address": mainnet_tether_addr},
    ],
}
