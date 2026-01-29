import pickle
import hashlib
import os
import time
import json

# -----------------------------
# Paths
# -----------------------------
SSE_INDEX_FILE = "sse_index/sse_index.pkl"
METRICS_FILE = "metrics/metrics_log.jsonl"

# -----------------------------
# Keyword encryption (SSE)
# -----------------------------
def encrypt_keyword(keyword):
    return hashlib.sha256(keyword.encode()).hexdigest()

# -----------------------------
# Query normalization
# -----------------------------
def normalize_query(query):
    q = query.lower().strip()
    keywords = []

    # Risk-based
    if "critical" in q:
        keywords.append("RISK_CRITICAL")
    if "high" in q:
        keywords.append("RISK_HIGH")
    if "normal" in q:
        keywords.append("RISK_NORMAL")

    # Date (YYYY-MM-DD)
    if "-" in q and len(q) >= 10:
        keywords.append(f"DATE_{q}")

    # Patient ID
    if "patient" in q:
        for part in q.split():
            if part.isdigit():
                keywords.append(f"PATIENT_{part}")

    return keywords

# -----------------------------
# Search API logic
# -----------------------------
def search_records(user_query):
    start_time = time.time()

    if not os.path.exists(SSE_INDEX_FILE):
        return []

    with open(SSE_INDEX_FILE, "rb") as f:
        sse_index = pickle.load(f)

    normalized_keywords = normalize_query(user_query)

    print("\nSEARCH DEBUG")
    print("User query        :", user_query)
    print("Normalized tokens :", normalized_keywords)

    result_sets = []

    for kw in normalized_keywords:
        enc_kw = encrypt_keyword(kw)
        if enc_kw in sse_index:
            result_sets.append(sse_index[enc_kw])

    if not result_sets:
        results = []
    else:
        results = list(set.intersection(*result_sets))

    end_time = time.time()
    total_time_ms = round((end_time - start_time) * 1000, 3)

    # -----------------------------
    # Metrics logging
    # -----------------------------
    metrics_entry = {
        "module": "SSE Search",
        "query": user_query,
        "normalized_keywords": len(normalized_keywords),
        "results_found": len(results),
        "search_time_ms": total_time_ms
    }

    os.makedirs("metrics", exist_ok=True)
    with open(METRICS_FILE, "a") as f:
        f.write(json.dumps(metrics_entry) + "\n")

    print("Results found     :", len(results))
    print(f"Search time       : {total_time_ms} ms")
    print("Metrics logged")

    return results
