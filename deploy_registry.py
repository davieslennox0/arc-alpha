import json
import os
from solcx import compile_source, install_solc
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

install_solc("0.8.19")

w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
WALLET = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CHAIN_ID = int(os.getenv("CHAIN_ID", 5042002))

with open("AgentRegistry.sol") as f:
    source = f.read()

compiled = compile_source(source, output_values=["abi", "bin"], solc_version="0.8.19")
contract_id = "<stdin>:AgentRegistry"
abi = compiled[contract_id]["abi"]
bytecode = compiled[contract_id]["bin"]

Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(WALLET, "pending")

tx = Contract.constructor().build_transaction({
    "from":     WALLET,
    "nonce":    nonce,
    "gas":      800000,
    "gasPrice": w3.eth.gas_price,
    "chainId":  CHAIN_ID,
})

signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"Deploying... tx: {tx_hash.hex()}")

receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
contract_address = receipt["contractAddress"]
print(f"Deployed at: {contract_address}")
print(f"Explorer: https://www.testnet.arcscan.app/address/{contract_address}")

# Save ABI and address
with open("registry_abi.json", "w") as f:
    json.dump(abi, f)
with open("registry_address.txt", "w") as f:
    f.write(contract_address)

print("Done. ABI saved to registry_abi.json")
