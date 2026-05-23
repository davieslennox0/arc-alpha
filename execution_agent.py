import os
import time
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv('/root/arc-alpha/.env')

for rpc in [os.getenv("RPC_URL"), "https://rpc.testnet.arc.network"]:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 30}))
        if w3.is_connected():
            break
    except Exception:
        continue

WALLET      = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CHAIN_ID    = int(os.getenv("CHAIN_ID", 5042002))

# Arc native stablecoins
USDC = Web3.to_checksum_address("0x3600000000000000000000000000000000000000")
EURC = Web3.to_checksum_address("0x89B50855Aa3bE2F677cD6303Cec089B5F319D72a")

ERC20_ABI = [
    {"inputs":[{"name":"recipient","type":"address"},{"name":"amount","type":"uint256"}],
     "name":"transfer","outputs":[{"name":"","type":"bool"}],
     "type":"function","stateMutability":"nonpayable"},
    {"inputs":[{"name":"account","type":"address"}],
     "name":"balanceOf","outputs":[{"name":"","type":"uint256"}],
     "type":"function","stateMutability":"view"},
    {"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],
     "name":"approve","outputs":[{"name":"","type":"bool"}],
     "type":"function","stateMutability":"nonpayable"},
]

def get_eurusd_rate() -> float:
    try:
        r = requests.get("https://api.frankfurter.app/latest?from=EUR&to=USD", timeout=5)
        return r.json()["rates"]["USD"]
    except Exception:
        return 1.08  # fallback

def get_balance(token_addr: str, wallet: str) -> float:
    token = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=ERC20_ABI)
    return token.functions.balanceOf(Web3.to_checksum_address(wallet)).call() / 1e6

def send_token(token_addr: str, to: str, amount: float, key: str, sender: str) -> str:
    token = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=ERC20_ABI)
    amount_wei = int(amount * 1e6)
    nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(sender), "pending")
    tx = token.functions.transfer(
        Web3.to_checksum_address(to), amount_wei
    ).build_transaction({
        "from":     Web3.to_checksum_address(sender),
        "nonce":    nonce,
        "gas":      100000,
        "gasPrice": w3.eth.gas_price,
        "chainId":  CHAIN_ID,
    })
    signed = w3.eth.account.sign_transaction(tx, key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    return tx_hash.hex()

def execute_fx_trade(asset: str, direction: str, amount_usdc: float,
                     agent_wallet: str, agent_key: str) -> dict:
    """
    FX settlement on Arc testnet:
    UP   → agent buys EURC with USDC  (long EUR/USD)
    DOWN → agent sells EURC for USDC  (short EUR/USD)
    """
    rate = get_eurusd_rate()

    if direction.upper() in ["UP", "BUY"]:
        eurc_amount = round(amount_usdc / rate, 6)

        # Agent sends USDC to broker
        tx1 = send_token(USDC, WALLET, amount_usdc, agent_key, agent_wallet)
        # Broker settles EURC to agent
        tx2 = send_token(EURC, agent_wallet, eurc_amount, PRIVATE_KEY, WALLET)

        return {
            "status":        "success",
            "type":          "FX_BUY",
            "pair":          "EURC/USDC",
            "rate":          rate,
            "usdc_spent":    amount_usdc,
            "eurc_received": eurc_amount,
            "asset":         asset,
            "direction":     direction,
            "tx_hash":       tx2,
            "tx_hash":       tx2,
            "tx_payment":    tx1,
            "tx_settlement": tx2,
            "explorer":      f"https://testnet.arcscan.app/tx/0x{tx2}"
        }

    else:
        eurc_amount = round(amount_usdc / rate, 6)
        eurc_bal    = get_balance(EURC, agent_wallet)

        # Use available EURC if below requested
        if eurc_bal < eurc_amount:
            eurc_amount = round(eurc_bal * 0.9, 6)

        usdc_received = round(eurc_amount * rate, 6)

        # Agent sends EURC to broker
        tx1 = send_token(EURC, WALLET, eurc_amount, agent_key, agent_wallet)
        # Broker settles USDC to agent
        tx2 = send_token(USDC, agent_wallet, usdc_received, PRIVATE_KEY, WALLET)

        return {
            "status":        "success",
            "type":          "FX_SELL",
            "pair":          "EURC/USDC",
            "rate":          rate,
            "eurc_spent":    eurc_amount,
            "usdc_received": usdc_received,
            "asset":         asset,
            "direction":     direction,
            "tx_hash":       tx2,
            "tx_hash":       tx2,
            "tx_payment":    tx1,
            "tx_settlement": tx2,
            "explorer":      f"https://testnet.arcscan.app/tx/0x{tx2}"
        }

if __name__ == "__main__":
    print(f"Connected:    {w3.is_connected()}")
    print(f"Broker:       {WALLET}")
    print(f"USDC balance: ${get_balance(USDC, WALLET):.4f}")
    print(f"EURC balance: €{get_balance(EURC, WALLET):.4f}")
    print(f"EUR/USD rate: {get_eurusd_rate()}")
    print("FX Execution Agent ready")
