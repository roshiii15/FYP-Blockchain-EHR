# retrieve_and_decrypt.py
import json
import os
import pickle
from web3 import Web3

# METRICS
import time

# prefer explicit ipfs connect to avoid version warning
try:
    import ipfshttpclient
    IPFS_AVAILABLE = True
except Exception:
    IPFS_AVAILABLE = False

from phe import paillier

# METRICS
retrieval_start = time.time()


# Load Paillier Keys (pickle)

with open("he_priv.pkl", "rb") as f:
    private_key = pickle.load(f)
public_key = private_key.public_key


# Connect to Ganache

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
if not w3.isConnected():
    print("Error: Ganache not connected at http://127.0.0.1:7545")
    exit(1)

with open("contract_addr.txt", "r", encoding="utf-8") as f:
    contract_address = f.read().strip()
with open("contract_abi.json", "r", encoding="utf-8") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)


def decrypt_field(entry):
    if entry is None:
        return None
    if isinstance(entry, dict) and "ct" in entry:
        ct_int = int(entry["ct"])
        enc_num = paillier.EncryptedNumber(public_key, ct_int)
        val = private_key.decrypt(enc_num)
        scale = int(entry.get("scale", 1))
        if scale != 1:
            return val / scale
        return val
    if isinstance(entry, list):
        out = []
        for e in entry:
            if isinstance(e, dict) and "ct" in e:
                ct_int = int(e["ct"])
                enc_num = paillier.EncryptedNumber(public_key, ct_int)
                v = private_key.decrypt(enc_num)
                scale = int(e.get("scale", 1))
                out.append(v / scale if scale != 1 else v)
            else:
                out.append(None)
        return out
    return None


# IPFS connect attempt 

ipfs_client = None
if IPFS_AVAILABLE:
    try:
        ipfs_client = ipfshttpclient.connect("/dns/localhost/tcp/5001/http")
    except Exception as e:
        print("IPFS client connect failed, using local fallback.")
        ipfs_client = None


# Get record id from user

record_id = input("Enter encrypted record ID (e.g., enc_rec_000012.json): ").strip()


# Fetch CID from blockchain

try:
    rec = contract.functions.getRecord(record_id).call()
    if isinstance(rec, (list, tuple)) and len(rec) >= 2:
        cid = rec[1]
    elif isinstance(rec, (list, tuple)) and len(rec) == 1:
        cid = rec[0]
    else:
        cid = str(rec)
    print("CID from blockchain:", cid)
except Exception as e:
    print("Could not get CID from blockchain:", e)
    exit(1)


# Retrieve encrypted JSON (IPFS or local fallback)

enc_data = None
if ipfs_client is not None:
    try:
        raw = ipfs_client.cat(cid)
        enc_data = json.loads(raw.decode())
    except Exception:
        enc_data = None

if enc_data is None:
    local_path = os.path.join("encrypted_blobs", record_id)
    if os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            enc_data = json.load(f)
    else:
        print("Encrypted file not found:", local_path)
        exit(1)

encrypted_section = enc_data.get("encrypted", enc_data)
meta = enc_data.get("meta", {})


# Decrypt fields

hr = decrypt_field(encrypted_section.get("heart_rate"))
temp = decrypt_field(encrypted_section.get("temperature"))
systolic = decrypt_field(encrypted_section.get("systolic"))
diastolic = decrypt_field(encrypted_section.get("diastolic"))

hr_val = hr[0] if isinstance(hr, list) and hr else hr
temp_val = temp[0] if isinstance(temp, list) and temp else temp
sys_val = systolic[0] if isinstance(systolic, list) and systolic else systolic
dia_val = diastolic[0] if isinstance(diastolic, list) and diastolic else diastolic


# Print results

print("\n===== Decrypted Patient Data =====")
print("Record ID     :", record_id)
if meta:
    print("Patient ID    :", meta.get("patient_id"))
    print("Timestamp     :", meta.get("timestamp"))
    print("Device ID     :", meta.get("device_id"))

if hr_val is not None:
    print(f"Heart Rate    : {hr_val} bpm")
if temp_val is not None:
    print(f"Temperature   : {temp_val} °C")
if sys_val is not None and dia_val is not None:
    print(f"Blood Pressure: {int(sys_val)}/{int(dia_val)} mmHg")

# METRICS

retrieval_end = time.time()
secure_retrieval_time_ms = (retrieval_end - retrieval_start) * 1000

os.makedirs("metrics", exist_ok=True)

metrics = {
    "module": "Secure Retrieval",
    "record_id": record_id,
    "secure_retrieval_time_ms": secure_retrieval_time_ms
}

with open("metrics/metrics_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(metrics) + "\n")

print("Secure retrieval metrics recorded")
print(f"Secure Retrieval Time (ms): {secure_retrieval_time_ms:.2f}")
