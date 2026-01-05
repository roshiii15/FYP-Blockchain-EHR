import json
from web3 import Web3
import time
import os

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not w3.isConnected():
    print("Error: Ganache not connected")
    exit()

print("Connected to Ganache")

with open("contract_addr.txt", "r") as f:
    contract_address = f.read().strip()

with open("contract_abi.json", "r") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)

with open("cid_map.json", "r") as f:
    cid_map = json.load(f)

account = w3.eth.accounts[0]

# METRICS
os.makedirs("metrics", exist_ok=True)
total_tx_time = 0
total_gas_used = 0
tx_count = 0

for recordId, cid in cid_map.items():
    print(f"Uploading -> {recordId} : {cid}")

    # METRICS
    tx_start = time.time()

    tx_hash = contract.functions.storeRecord(
        recordId,
        cid
    ).transact({'from': account})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # METRICS
    tx_end = time.time()

    tx_time = tx_end - tx_start
    gas_used = receipt.gasUsed

    total_tx_time += tx_time
    total_gas_used += gas_used
    tx_count += 1

    print(f"Stored | Block: {receipt.blockNumber} | Time: {tx_time:.3f}s | Gas: {gas_used}")

# METRICS
average_tx_time = total_tx_time / tx_count if tx_count > 0 else 0
average_gas_used = total_gas_used / tx_count if tx_count > 0 else 0
throughput = tx_count / total_tx_time if total_tx_time > 0 else 0

metrics = {
    "module": "Blockchain Storage",
    "total_transactions": tx_count,
    "total_transaction_time_sec": total_tx_time,
    "average_transaction_time_sec": average_tx_time,
    "total_gas_used": total_gas_used,
    "average_gas_used": average_gas_used,
    "throughput_tx_per_sec": throughput
}

with open("metrics/metrics_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(metrics) + "\n")

print("\nAll CIDs stored on blockchain successfully")
print("Blockchain metrics recorded")
