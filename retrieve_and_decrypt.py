# retrieve_and_decrypt.py
import json
import os
import pickle
from web3 import Web3

# prefer explicit ipfs connect to avoid version warning
try:
    import ipfshttpclient
    IPFS_AVAILABLE = True
except Exception:
    IPFS_AVAILABLE = False

from phe import paillier

# -------------------------------
# Load Paillier Keys (pickle)
# -------------------------------
with open("he_priv.pkl", "rb") as f:
    private_key = pickle.load(f)
public_key = private_key.public_key

# -------------------------------
# Connect to Ganache
# -------------------------------
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
if not w3.isConnected():
    print("❌ Error: Ganache not connected at http://127.0.0.1:7545")
    exit(1)

with open("contract_addr.txt", "r", encoding="utf-8") as f:
    contract_address = f.read().strip()
with open("contract_abi.json", "r", encoding="utf-8") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)

# -------------------------------
# Helper: decrypt a single encrypted-field entry
# Field format (observed): {"ct": "<big-int-as-string>", "scale": <int>}
# or sometimes a list of such dicts.
# -------------------------------
def decrypt_field(entry):
    if entry is None:
        return None
    # single dict with 'ct'
    if isinstance(entry, dict) and "ct" in entry:
        ct_int = int(entry["ct"])
        enc_num = paillier.EncryptedNumber(public_key, ct_int)
        val = private_key.decrypt(enc_num)
        scale = int(entry.get("scale", 1))
        if scale != 1:
            return val / scale
        return val
    # list of entries (decrypt each)
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
    # unexpected format
    return None

# -------------------------------
# IPFS connect attempt (preferred)
# -------------------------------
ipfs_client = None
if IPFS_AVAILABLE:
    try:
        ipfs_client = ipfshttpclient.connect("/dns/localhost/tcp/5001/http")
        # note: you may still get a VersionMismatch warning but connection works
    except Exception as e:
        print("⚠ IPFS client connect failed (will fallback to local). Reason:", e)
        ipfs_client = None
else:
    print("⚠ ipfshttpclient not installed; script will use local encrypted_blobs/ files if available.")

# -------------------------------
# Get record id from user
# -------------------------------
record_id = input("Enter encrypted record ID (e.g., enc_rec_000012.json): ").strip()

# -------------------------------
# Fetch CID from blockchain
# -------------------------------
try:
    # our contract.getRecord(recordId) returns (recordId, cid) in the 2-param contract
    rec = contract.functions.getRecord(record_id).call()
    # rec may be a tuple: (recordId, cid) or (cid,) depending on contract version
    if isinstance(rec, (list, tuple)) and len(rec) >= 2:
        cid = rec[1]
    elif isinstance(rec, (list, tuple)) and len(rec) == 1:
        cid = rec[0]
    else:
        # fallback: try to interpret as string
        cid = str(rec)
    print("✔ CID from blockchain:", cid)
except Exception as e:
    print("❌ Could not get CID from blockchain for", record_id, " — error:", e)
    exit(1)

# -------------------------------
# Retrieve encrypted JSON (IPFS or local fallback)
# -------------------------------
enc_data = None
# Try IPFS first (if available)
if ipfs_client is not None:
    try:
        print("Fetching encrypted data from IPFS...")
        raw = ipfs_client.cat(cid)
        enc_data = json.loads(raw.decode())
    except Exception as e:
        print("⚠ Could not fetch from IPFS (will fallback to local file). Reason:", e)
        enc_data = None

# Fallback: local file encrypted_blobs/<record_id>
if enc_data is None:
    local_path = os.path.join("encrypted_blobs", record_id)
    if os.path.exists(local_path):
        print("Loading encrypted data from local file:", local_path)
        with open(local_path, "r", encoding="utf-8") as f:
            enc_data = json.load(f)
    else:
        print("❌ Encrypted file not found on IPFS nor locally:", local_path)
        exit(1)

# -------------------------------
# DEBUG: show top-level keys (optional)
# -------------------------------
print("DEBUG: Top-level keys in encrypted JSON:", list(enc_data.keys()))

# Your structure is: { "meta": {...}, "encrypted": {...} }
encrypted_section = enc_data.get("encrypted", enc_data)  # if top-level is already encrypted
meta = enc_data.get("meta", {})

# -------------------------------
# Decrypt fields (use observed keys)
# -------------------------------
# keys found in your sample: heart_rate, temperature, systolic, diastolic
hr = decrypt_field(encrypted_section.get("heart_rate"))
temp = decrypt_field(encrypted_section.get("temperature"))
systolic = decrypt_field(encrypted_section.get("systolic"))
diastolic = decrypt_field(encrypted_section.get("diastolic"))

# In case any field produced a list, take first element for single-value fields
if isinstance(hr, list):
    hr_val = hr[0] if len(hr) > 0 else None
else:
    hr_val = hr
if isinstance(temp, list):
    temp_val = temp[0] if len(temp) > 0 else None
else:
    temp_val = temp
if isinstance(systolic, list):
    sys_val = systolic[0] if len(systolic) > 0 else None
else:
    sys_val = systolic
if isinstance(diastolic, list):
    dia_val = diastolic[0] if len(diastolic) > 0 else None
else:
    dia_val = diastolic

# -------------------------------
# Print results
# -------------------------------
print("\n===== Decrypted Patient Data =====")
print("Record ID     :", record_id)
if meta:
    print("Patient ID    :", meta.get("patient_id"))
    print("Timestamp     :", meta.get("timestamp"))
    print("Device ID     :", meta.get("device_id"))

if hr_val is not None:
    print(f"Heart Rate    : {hr_val} bpm")
else:
    print("Heart Rate    : <not present>")

if temp_val is not None:
    print(f"Temperature   : {temp_val} °C")
else:
    print("Temperature   : <not present>")

if sys_val is not None and dia_val is not None:
    print(f"Blood Pressure: {int(sys_val)}/{int(dia_val)} mmHg")
else:
    print("Blood Pressure: <not present>")

# Print any other encrypted keys found (non-standard)
other_keys = [k for k in encrypted_section.keys() if k not in ("heart_rate", "temperature", "systolic", "diastolic")]
if other_keys:
    print("\nOther encrypted fields present:", other_keys)
    for k in other_keys:
        val = decrypt_field(encrypted_section.get(k))
        print(f"{k} => {val}")
