import json
import os
import hashlib
import pickle
import time
from collections import defaultdict

# -----------------------------
# Paths
# -----------------------------
ANOMALY_FILE = "anomaly_results.json"

SSE_DIR = "sse_index"
INDEX_FILE = os.path.join(SSE_DIR, "sse_index.pkl")

METRICS_DIR = "metrics"
METRICS_FILE = os.path.join(METRICS_DIR, "metrics_log.jsonl")

os.makedirs(SSE_DIR, exist_ok=True)
os.makedirs(METRICS_DIR, exist_ok=True)

# -----------------------------
# Keyword Hash (acts as SSE encryption)
# -----------------------------
def encrypt_keyword(keyword):
    return hashlib.sha256(keyword.encode()).hexdigest()

# -----------------------------
# Load anomaly detection output
# -----------------------------
with open(ANOMALY_FILE, "r") as f:
    anomaly_data = json.load(f)

# -----------------------------
# SSE Index structure
# -----------------------------
sse_index = defaultdict(set)

total_keywords = 0
start_time = time.time()

# -----------------------------
# Build SSE Index
# -----------------------------
for record_file, data in anomaly_data.items():

    record_id = record_file.replace(".json", "")

    patient_id = data["patient_id"]
    risk = data["risk_level"]
    device_id = data["device_id"]
    date = data["timestamp"].split("T")[0]

    keywords = []

    # ---- Risk keywords ----
    keywords.append(f"RISK_{risk}")
    keywords.append(risk.lower())
    keywords.append("risk")

    # ---- Patient keywords ----
    keywords.append(f"PATIENT_{patient_id}")
    keywords.append("patient")
    keywords.append(str(patient_id).lower())

    # ---- Device keywords ----
    keywords.append(f"DEVICE_{device_id}")
    keywords.append("device")
    keywords.append(str(device_id).lower())

    # ---- Date keywords ----
    keywords.append(f"DATE_{date}")
    keywords.append("date")


    total_keywords += len(keywords)

    for word in keywords:
        enc_word = encrypt_keyword(word)
        sse_index[enc_word].add(record_id)

end_time = time.time()
total_time = end_time - start_time
avg_time = total_time / len(anomaly_data)

# -----------------------------
# Save SSE Index
# -----------------------------
with open(INDEX_FILE, "wb") as f:
    pickle.dump(dict(sse_index), f)

# -----------------------------
# Compute Index Size
# -----------------------------
index_size_kb = os.path.getsize(INDEX_FILE) / 1024

# -----------------------------
# Append Metrics
# -----------------------------
metrics_entry = {
    "module": "SSE Index Building",
    "records_indexed": len(anomaly_data),
    "total_keywords_indexed": total_keywords,
    "unique_encrypted_keywords": len(sse_index),
    "average_keywords_per_record": round(total_keywords / len(anomaly_data), 2),
    "total_index_build_time_ms": round(total_time * 1000, 2),
    "average_index_time_per_record_ms": round(avg_time * 1000, 4),
    "index_size_kb": round(index_size_kb, 2)
}

with open(METRICS_FILE, "a") as f:
    f.write(json.dumps(metrics_entry) + "\n")

print("SSE index built successfully")
print(f"Records indexed      : {len(anomaly_data)}")
print(f"Unique keywords      : {len(sse_index)}")
print(f"Index size           : {index_size_kb:.2f} KB")
print(f"Total build time     : {total_time:.3f} s")
print("📊 Metrics appended to metrics_log.jsonl")
