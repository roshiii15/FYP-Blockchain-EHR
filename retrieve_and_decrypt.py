
import time, json, pickle, subprocess
from phe import paillier

METRICS = "metrics/metrics_log.jsonl"

with open("he_priv.pkl", "rb") as f:
    private_key = pickle.load(f)

def retrieve_and_decrypt_record(cid):
    start = time.time()

    result = subprocess.run(["ipfs", "cat", cid], capture_output=True, text=True)
    record = json.loads(result.stdout)

    decrypted = {}
    for k, v in record["encrypted"].items():
        enc = paillier.EncryptedNumber(private_key.public_key, int(v["ct"]))
        decrypted[k] = private_key.decrypt(enc) / v.get("scale", 1)

    end = time.time()

    with open(METRICS, "a") as f:
        f.write(json.dumps({
            "module": "Retrieve+Decrypt",
            "cid": cid,
            "time_ms": round((end - start)*1000, 2)
        }) + "\n")
    
    print("Decryption completed")

    return decrypted
