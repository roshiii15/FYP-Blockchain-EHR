import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not w3.isConnected():
    print("❌ Error: Ganache not connected")
    exit()

print("✓ Connected to Ganache")

with open("contract_addr.txt", "r") as f:
    contract_address = f.read().strip()

with open("contract_abi.json", "r") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)

with open("cid_map.json", "r") as f:
    cid_map = json.load(f)

account = w3.eth.accounts[0]

for recordId, cid in cid_map.items():
    print(f"Uploading → {recordId} : {cid}")

    tx_hash = contract.functions.storeRecord(
        recordId,
        cid
    ).transact({'from': account})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"✓ Stored | Block: {receipt.blockNumber}")

print("\n🎉 All CIDs stored on blockchain successfully!")
