# ipfs_upload.py
import os
import json
import hashlib
import time

ENC_DIR = "encrypted_blobs"
CID_MAP_FILE = "cid_map.json"


# TRY CONNECTING TO IPFS DESKTOP
use_ipfs = False

try:
    import ipfshttpclient
    
    # This works if IPFS Desktop daemon is running
    client = ipfshttpclient.connect("/dns/localhost/tcp/5001/http")
    use_ipfs = True
    print("Connected to IPFS Desktop (API port 5001).")
except Exception as e:
    print("Could not connect to IPFS API. Falling back to SHA256 simulation.")
    print("Reason:", e)
    use_ipfs = False


# PROCESS ENCRYPTED FILES
files = sorted(f for f in os.listdir(ENC_DIR) if f.endswith(".json"))
cid_map = {}

print(f"\nUploading {len(files)} encrypted records...\n")

# METRICS
upload_start = time.time()
successful_uploads = 0
failed_uploads = 0
total_bytes_uploaded = 0

for filename in files:
    full_path = os.path.join(ENC_DIR, filename)
    file_size = os.path.getsize(full_path)
    total_bytes_uploaded += file_size

    if use_ipfs:
        # IPFS UPLOAD
        try:
            res = client.add(full_path)
            cid = res["Hash"]
            successful_uploads += 1
            print(f"Uploaded {filename} -> CID: {cid}")
        except Exception as e:
            failed_uploads += 1
            print(f"Upload failed for {filename}, switching to SHA256.")
            with open(full_path, "rb") as f:
                cid = hashlib.sha256(f.read()).hexdigest()
            print(f"Simulated CID for {filename}: {cid}")
    else:
        # FALLBACK (NO IPFS API)
        with open(full_path, "rb") as f:
            cid = hashlib.sha256(f.read()).hexdigest()
        successful_uploads += 1
        print(f"Simulated CID for {filename}: {cid}")

    cid_map[filename] = cid

# METRICS
upload_end = time.time()
total_upload_time_ms = (upload_end - upload_start) * 1000
average_upload_time_ms = total_upload_time_ms / len(files)


# SAVE cid_map.json

with open(CID_MAP_FILE, "w") as outfile:
    json.dump(cid_map, outfile, indent=4)

# METRICS
os.makedirs("metrics", exist_ok=True)

metrics = {
    "module": "IPFS Storage",
    "storage_mode": "IPFS" if use_ipfs else "Simulated",
    "total_files": len(files),
    "successful_uploads": successful_uploads,
    "failed_uploads": failed_uploads,
    "total_upload_time_ms": total_upload_time_ms,
    "average_upload_time_ms": average_upload_time_ms,
    "total_data_uploaded_bytes": total_bytes_uploaded
}

with open("metrics/metrics_log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(metrics) + "\n")

print("\nUpload complete.")
print(f"CID map saved to: {CID_MAP_FILE}")
print("IPFS metrics recorded.")
