from web3 import Web3
import json

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

assert w3.isConnected(), "Ganache not connected"

# Load ABI & Bytecode
with open("contract_abi.json") as f:
    abi = json.load(f)

with open("contract_bytecode.txt") as f:
    bytecode = f.read()

# Account
account = w3.eth.accounts[0]

# Contract object
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Deploy
tx_hash = Contract.constructor().transact({
    "from": account,
    "gas": 6000000
})

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Save contract address
with open("contract_addr.txt", "w") as f:
    f.write(tx_receipt.contractAddress)

print("Contract deployed at:", tx_receipt.contractAddress)
