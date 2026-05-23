import os
import time
import logging
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("Refill")

w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
CHAIN_ID = int(os.getenv("CHAIN_ID", 5042002))
BROKER_KEY = os.getenv("PRIVATE_KEY")
BROKER_WALLET = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
USDC = Web3.to_checksum_address("0x3600000000000000000000000000000000000000")

AGENT_WALLETS = [
    Web3.to_checksum_address(os.getenv("AGENT_ALICE_ADDRESS")),
    Web3.to_checksum_address(os.getenv("AGENT_BOB_ADDRESS")),
    Web3.to_checksum_address(os.getenv("AGENT_CHARLIE_ADDRESS")),
]

REFILL_THRESHOLD = 0.05  # refill when below this
REFILL_AMOUNT    = 0.30   # send this much
MIN_BROKER_USDT  = 1.0    # don't refill if broker is below this

ERC20_ABI = [
    {"inputs":[{"name":"account","type":"address"}],
     "name":"balanceOf","outputs":[{"name":"","type":"uint256"}],
     "type":"function","stateMutability":"view"},
    {"inputs":[{"name":"to","type":"address"},{"name":"amount","type":"uint256"}],
     "name":"transfer","outputs":[{"name":"","type":"bool"}],
     "type":"function","stateMutability":"nonpayable"}
]

def get_usdc(address):
    usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)
    return usdc.functions.balanceOf(address).call() / 1e6

def send_usdc(to, amount):
    usdc = w3.eth.contract(address=USDC, abi=ERC20_ABI)
    amount_wei = int(amount * 1e6)
    nonce = w3.eth.get_transaction_count(BROKER_WALLET)
    tx = usdc.functions.transfer(to, amount_wei).build_transaction({
        "from":     BROKER_WALLET,
        "nonce":    nonce,
        "gas":      100000,
        "gasPrice": w3.eth.gas_price,
        "chainId":  CHAIN_ID,
    })
    signed = w3.eth.account.sign_transaction(tx, BROKER_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    return tx_hash.hex() if receipt["status"] == 1 else None

def check_and_refill():
    broker_bal = get_usdc(BROKER_WALLET)
    if broker_bal < MIN_BROKER_USDT:
        log.info(f"Broker too low (${broker_bal:.4f}) — skipping refill")
        return

    for addr in AGENT_WALLETS:
        bal = get_usdc(addr)
        if bal <= REFILL_THRESHOLD:
            log.info(f"Refilling {addr[:10]}... (${bal:.4f}) → +${REFILL_AMOUNT}")
            tx = send_usdc(addr, REFILL_AMOUNT)
            if tx:
                log.info(f"Refill tx: {tx}")
            else:
                log.info(f"Refill failed for {addr[:10]}...")

def run():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(message)s",
        handlers=[
            logging.FileHandler("refill.log"),
            logging.StreamHandler()
        ]
    )
    log.info("Auto-refill service started")
    while True:
        try:
            check_and_refill()
        except Exception as e:
            log.error(f"Refill error: {e}")
        time.sleep(120)  # check every 2 minutes

if __name__ == "__main__":
    run()
