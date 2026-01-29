# blockchain_access.py
import json
import time
from web3 import Web3

GANACHE_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

METRICS = "metrics/metrics_log.jsonl"


def request_access_from_blockchain(contract, record_id, role, emergency, account):
    start = time.time()

    tx = contract.functions.getCID(
        record_id,
        role,
        emergency
    ).transact({"from": account})

    receipt = w3.eth.wait_for_transaction_receipt(tx)

    # READ RETURN VALUE FROM EVENT LOGS IS NOT POSSIBLE
    # So we fetch CID AFTER tx using VIEW CALL (safe now)

    cid = contract.functions.getCIDView(record_id).call()

    end = time.time()

    with open(METRICS, "a") as f:
        f.write(json.dumps({
            "module": "Blockchain Access",
            "record_id": record_id,
            "role": role,
            "emergency": emergency,
            "latency_ms": round((end - start) * 1000, 2)
        }) + "\n")

    print("Blockchain: ACCESS GRANTED")

    return cid

