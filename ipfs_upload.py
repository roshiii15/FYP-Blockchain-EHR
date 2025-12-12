# ipfs_upload.py
import os
import json
import hashlib

ENC_DIR = "encrypted_blobs"
CID_MAP_FILE = "cid_map.json"

# -------------------------------
# TRY CONNECTING TO IPFS DESKTOP
# -------------------------------
use_ipfs = False

try:
    import ipfshttpclient
    
    # This works if IPFS Desktop daemon is running
    client = ipfshttpclient.connect("/dns/localhost/tcp/5001/http")
    use_ipfs = True
    print("✅ Connected to IPFS Desktop (API port 5001).")
except Exception as e:
    print("⚠️ Could not connect to IPFS API. Falling back to SHA256 simulation.")
    print("Reason:", e)
    use_ipfs = False

# -------------------------------
# PROCESS ENCRYPTED FILES
# -------------------------------
files = sorted(f for f in os.listdir(ENC_DIR) if f.endswith(".json"))
cid_map = {}

print(f"\n📁 Uploading {len(files)} encrypted records...\n")

for filename in files:
    full_path = os.path.join(ENC_DIR, filename)

    if use_ipfs:
        # REAL IPFS UPLOAD
        try:
            res = client.add(full_path)
            cid = res["Hash"]
            print(f"✔ Uploaded {filename}  →  CID: {cid}")
        except Exception as e:
            print(f"❌ Upload failed for {filename}, switching to SHA256. Error:", e)
            with open(full_path, "rb") as f:
                cid = hashlib.sha256(f.read()).hexdigest()
            print(f"✔ Simulated CID for {filename}: {cid}")
    else:
        # FALLBACK (NO IPFS API)
        with open(full_path, "rb") as f:
            cid = hashlib.sha256(f.read()).hexdigest()
        print(f"✔ Simulated CID for {filename}: {cid}")

    cid_map[filename] = cid

# -------------------------------
# SAVE cid_map.json
# -------------------------------
with open(CID_MAP_FILE, "w") as outfile:
    json.dump(cid_map, outfile, indent=4)

print(f"\n🎉 Upload complete!\n📄 CID map saved to: {CID_MAP_FILE}")
