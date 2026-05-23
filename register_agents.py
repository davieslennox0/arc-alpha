import json, os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
WALLET = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CHAIN_ID = int(os.getenv("CHAIN_ID", 5042002))
REGISTRY = Web3.to_checksum_address(os.getenv("REGISTRY_ADDRESS"))

with open("registry_abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=REGISTRY, abi=abi)

# Register 4 internal agents + 3 external agents
agents = [
    ("scout",     WALLET),
    ("risk",      WALLET),
    ("learning",  WALLET),
    ("execution", WALLET),
    ("alice",     Web3.to_checksum_address(os.getenv("AGENT_ALICE_ADDRESS"))),
    ("bob",       Web3.to_checksum_address(os.getenv("AGENT_BOB_ADDRESS"))),
    ("charlie",   Web3.to_checksum_address(os.getenv("AGENT_CHARLIE_ADDRESS"))),
]

for agent_id, wallet in agents:
    nonce = w3.eth.get_transaction_count(WALLET, "pending")
    tx = contract.functions.registerAgent(agent_id, wallet).build_transaction({
        "from": WALLET, "nonce": nonce,
        "gas": 200000, "gasPrice": w3.eth.gas_price, "chainId": CHAIN_ID
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
    print(f"Registered {agent_id}: {tx_hash.hex()}")

print(f"\nAll agents registered!")
print(f"Registry: https://www.testnet.arcscan.app/address/{REGISTRY}")
