import os
import time
import logging
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv('/root/arc-alpha/.env')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler("/root/arc-alpha/agents.log"),
        logging.StreamHandler()
    ]
)

for rpc in [os.getenv("RPC_URL"), "https://rpc.testnet.arc.network"]:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 30}))
        if w3.is_connected():
            break
    except Exception:
        continue

CHAIN_ID     = int(os.getenv("CHAIN_ID", 5042002))
BROKER_URL   = "http://localhost:8002"
BROKER_WALLET = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))

USDC = Web3.to_checksum_address("0x3600000000000000000000000000000000000000")

ERC20_ABI = [
    {"inputs":[{"name":"account","type":"address"}],
     "name":"balanceOf","outputs":[{"name":"","type":"uint256"}],
     "type":"function","stateMutability":"view"},
    {"inputs":[{"name":"to","type":"address"},{"name":"amount","type":"uint256"}],
     "name":"transfer","outputs":[{"name":"","type":"bool"}],
     "type":"function","stateMutability":"nonpayable"}
]

AGENTS = [
    {"name": "Alice",   "address": os.getenv("AGENT_ALICE_ADDRESS"),   "key": os.getenv("AGENT_ALICE_KEY"),   "asset": "EURUSD", "interval": 300},
    {"name": "Bob",     "address": os.getenv("AGENT_BOB_ADDRESS"),     "key": os.getenv("AGENT_BOB_KEY"),     "asset": "EURUSD", "interval": 360},
    {"name": "Charlie", "address": os.getenv("AGENT_CHARLIE_ADDRESS"), "key": os.getenv("AGENT_CHARLIE_KEY"), "asset": "EURUSD", "interval": 420},
]

CYCLES = {"Alice": 0, "Bob": 0, "Charlie": 0}

def get_usdc_balance(address):
    usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)
    return usdc.functions.balanceOf(Web3.to_checksum_address(address)).call() / 1e6

def pay_broker(agent, amount):
    usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)
    amount_wei = int(amount * 1e6)
    nonce = w3.eth.get_transaction_count(Web3.to_checksum_address(agent["address"]), "pending")
    tx = usdc.functions.transfer(BROKER_WALLET, amount_wei).build_transaction({
        "from":     Web3.to_checksum_address(agent["address"]),
        "nonce":    nonce,
        "gas":      100000,
        "gasPrice": w3.eth.gas_price,
        "chainId":  CHAIN_ID,
    })
    signed = w3.eth.account.sign_transaction(tx, agent["key"])
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    return tx_hash.hex()

def run_agent(agent):
    log = logging.getLogger(agent["name"])
    log.info(f"Agent starting — asset: {agent['asset']} | interval: {agent['interval']}s")

    while True:
        try:
            bal = get_usdc_balance(agent["address"])
            log.info(f"Balance: ${bal:.4f} USDC | Scanning {agent['asset']}...")

            if bal < 0.10:
                log.warning("Low balance — skipping cycle")
                time.sleep(agent["interval"])
                continue

            # Pay broker fee
            fee = 0.05
            log.info(f"Paying ${fee} x402 fee to broker...")
            tx_hash = pay_broker(agent, fee)
            log.info(f"Payment tx: {tx_hash}")

            # Alternate direction each cycle
            cycle = CYCLES[agent["name"]]
            direction = "UP" if cycle % 2 == 0 else "DOWN"
            CYCLES[agent["name"]] += 1

            # Call broker execute
            res = requests.post(f"{BROKER_URL}/execute", json={
                "asset":       agent["asset"],
                "direction":   direction,
                "amount_usdt": 0.50,
                "agent_id":    agent["name"].lower(),
                "tx_hash":     tx_hash
            }, timeout=60)

            result = res.json()
            if not isinstance(result, dict):
                log.error(f"Unexpected response: {result}")
                time.sleep(agent["interval"])
                continue

            status = result.get("status", "unknown")
            log.info(f"Response: {status} | direction: {direction}")

            if status == "success":
                log.info(f"FX trade executed: {result.get('explorer', '')}")
            else:
                log.info(f"Not executed: {result.get('reason', result.get('detail', str(result)))}")

        except Exception as e:
            log.error(f"Agent error: {e}")

        time.sleep(agent["interval"])

if __name__ == "__main__":
    import threading
    threads = []
    for agent in AGENTS:
        t = threading.Thread(target=run_agent, args=(agent,), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(5)

    for t in threads:
        t.join()
