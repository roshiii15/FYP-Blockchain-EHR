import os
import json
import pickle
import time
from phe import paillier

# -----------------------------
# Load Paillier Keys
# -----------------------------
with open("he_pub.pkl", "rb") as f:
    public_key = pickle.load(f)

with open("he_priv.pkl", "rb") as f:
    private_key = pickle.load(f)

# -----------------------------
# Input / Output paths
# -----------------------------
ENC_DIR = "encrypted_blobs"
OUTPUT_FILE = "anomaly_results.json"

METRICS_DIR = "metrics"
METRICS_FILE = os.path.join(METRICS_DIR, "metrics_log.jsonl")

results = {}

normal_count = 0
high_risk_count = 0
critical_count = 0

start_time = time.time()

# -----------------------------
# Define normal thresholds (PLAINTEXT)
# -----------------------------
THRESHOLDS = {
    "heart_rate": (60, 100),
    "temperature": (36.1, 37.5),   # °C (will be scaled dynamically)
    "systolic": (90, 120)
}

# -----------------------------
# Function to calculate overall risk
# -----------------------------
def evaluate_risk(hr_risk, temp_risk, bp_risk):
    risks = [hr_risk, temp_risk, bp_risk]
    critical_count = risks.count("CRITICAL")

    if critical_count >= 2:
        return "CRITICAL"
    elif critical_count == 1:
        return "HIGH"
    else:
        return "NORMAL"

# -----------------------------
# Process encrypted records
# -----------------------------
for file in sorted(os.listdir(ENC_DIR)):
    if not file.endswith(".json"):
        continue

    with open(os.path.join(ENC_DIR, file), "r") as f:
        record = json.load(f)

    # -----------------------------
    # Load encrypted values
    # -----------------------------
    enc_hr = paillier.EncryptedNumber(
        public_key, int(record["encrypted"]["heart_rate"]["ct"])
    )

    enc_bp = paillier.EncryptedNumber(
        public_key, int(record["encrypted"]["systolic"]["ct"])
    )

    # -------- TEMPERATURE (scale-aware) --------
    temp_ct = int(record["encrypted"]["temperature"]["ct"])
    temp_scale = record["encrypted"]["temperature"]["scale"]

    enc_temp = paillier.EncryptedNumber(public_key, temp_ct)

    # -----------------------------
    # Encrypt thresholds correctly
    # -----------------------------
    # HR
    hr_low, hr_high = THRESHOLDS["heart_rate"]
    enc_hr_low = public_key.encrypt(hr_low)
    enc_hr_high = public_key.encrypt(hr_high)

    # BP
    bp_low, bp_high = THRESHOLDS["systolic"]
    enc_bp_low = public_key.encrypt(bp_low)
    enc_bp_high = public_key.encrypt(bp_high)

    # TEMP (scaled)
    temp_low, temp_high = THRESHOLDS["temperature"]
    enc_temp_low = public_key.encrypt(int(temp_low * temp_scale))
    enc_temp_high = public_key.encrypt(int(temp_high * temp_scale))

    # -----------------------------
    # Compute encrypted differences
    # -----------------------------
    hr_low_diff = private_key.decrypt(enc_hr - enc_hr_low)
    hr_high_diff = private_key.decrypt(enc_hr - enc_hr_high)

    bp_low_diff = private_key.decrypt(enc_bp - enc_bp_low)
    bp_high_diff = private_key.decrypt(enc_bp - enc_bp_high)

    temp_low_diff = private_key.decrypt(enc_temp - enc_temp_low)
    temp_high_diff = private_key.decrypt(enc_temp - enc_temp_high)

    # -----------------------------
    # Parameter-level risk
    # -----------------------------
    param_risks = {}

    # Heart Rate
    if hr_low_diff < -15 or hr_high_diff > 15:
        param_risks["heart_rate"] = "CRITICAL"
    elif hr_low_diff < -5 or hr_high_diff > 5:
        param_risks["heart_rate"] = "HIGH"
    else:
        param_risks["heart_rate"] = "NORMAL"

    # Temperature (scaled logic)
    if temp_low_diff < -(1 * temp_scale) or temp_high_diff > (1 * temp_scale):
        param_risks["temperature"] = "CRITICAL"
    elif temp_low_diff < -(0.5 * temp_scale) or temp_high_diff > (0.5 * temp_scale):
        param_risks["temperature"] = "HIGH"
    else:
        param_risks["temperature"] = "NORMAL"

    # Systolic BP
    if bp_low_diff < -15 or bp_high_diff > 15:
        param_risks["systolic"] = "CRITICAL"
    elif bp_low_diff < -5 or bp_high_diff > 5:
        param_risks["systolic"] = "HIGH"
    else:
        param_risks["systolic"] = "NORMAL"

    # -----------------------------
    # Overall risk
    # -----------------------------
    overall_risk = evaluate_risk(
        param_risks["heart_rate"],
        param_risks["temperature"],
        param_risks["systolic"]
    )

    if overall_risk == "NORMAL":
        normal_count += 1
    elif overall_risk == "HIGH":
        high_risk_count += 1
    else:
        critical_count += 1

    # -----------------------------
    # Store result
    # -----------------------------
    results[file] = {
        "patient_id": record["meta"]["patient_id"],
        "timestamp": record["meta"]["timestamp"],
        "device_id": record["meta"]["device_id"],
        "risk_level": overall_risk,
        "param_risks": param_risks
    }

end_time = time.time()
total_time = end_time - start_time
avg_time = total_time / len(results)

# -----------------------------
# Save anomaly results
# -----------------------------
with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=4)

# -----------------------------
# Append metrics
# -----------------------------
os.makedirs(METRICS_DIR, exist_ok=True)

metrics_entry = {
    "module": "Encrypted Anomaly Detection",
    "records_processed": len(results),
    "normal_records": normal_count,
    "high_risk_records": high_risk_count,
    "critical_records": critical_count,
    "total_detection_time_ms": total_time * 1000,
    "average_time_per_record_ms": avg_time * 1000
}

with open(METRICS_FILE, "a") as f:
    f.write(json.dumps(metrics_entry) + "\n")

print("Encrypted anomaly detection completed")
print(f"Records processed: {len(results)}")
print(f"Normal: {normal_count}, High Risk: {high_risk_count}, Critical: {critical_count}")
print(f"Total Time: {total_time:.2f}s | Avg per record: {avg_time:.4f}s")
print("Metrics appended to metrics_log.jsonl")
