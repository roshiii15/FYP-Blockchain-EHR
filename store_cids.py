import json
import time
import os
from blockchain_interface import contract, w3

METRICS_DIR = "metrics"
METRICS_FILE = os.path.join(METRICS_DIR, "metrics_log.jsonl")
os.makedirs(METRICS_DIR, exist_ok=True)

with open("cid_map.json") as f:
    cid_map = json.load(f)

tx_count = 0
total_gas = 0

start_time = time.time()

for record_id, cid in cid_map.items():
    tx_hash = contract.functions.storeRecord(record_id, cid).transact()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    tx_count += 1
    total_gas += receipt.gasUsed

end_time = time.time()

total_time = end_time - start_time
avg_latency = (total_time / tx_count) * 1000
throughput = tx_count / total_time
avg_gas = total_gas / tx_count

metrics_entry = {
    "module": "Blockchain CID Storage",
    "total_transactions": tx_count,
    "total_time_ms": total_time * 1000,
    "average_latency_ms": avg_latency,
    "throughput_tps": throughput,
    "total_gas_used": total_gas,
    "average_gas_per_tx": avg_gas
}

with open(METRICS_FILE, "a") as f:
    f.write(json.dumps(metrics_entry) + "\n")

print("Blockchain CID storage completed with aggregated metrics")
