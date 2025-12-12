# deploy_contract.py
from solcx import compile_standard, install_solc
from web3 import Web3
import json

# Install compiler (first time only). Safe to run everytime.
install_solc('0.8.0')

# Load contract source
with open("EHRRegistry.sol", "r", encoding="utf-8") as f:
    source = f.read()

# Compile
compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"EHRRegistry.sol": {"content": source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode"]}
            }
        },
    },
    solc_version="0.8.0"
)

abi = compiled["contracts"]["EHRRegistry.sol"]["EHRRegistry"]["abi"]
bytecode = compiled["contracts"]["EHRRegistry.sol"]["EHRRegistry"]["evm"]["bytecode"]["object"]

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
acct = w3.eth.accounts[0]

# Deploy
contract = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = contract.constructor().transact({'from': acct})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress
print("Contract deployed at:", contract_address)

# Save ABI + address
with open("contract_abi.json", "w") as f:
    json.dump(abi, f)

with open("contract_addr.txt", "w") as f:
    f.write(contract_address)

print("Saved ABI & contract address.")
