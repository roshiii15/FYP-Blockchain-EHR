from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import json
import os
import hashlib

# Your modules
from search_api import search_records
from blockchain_access import request_access_from_blockchain
from retrieve_and_decrypt import retrieve_and_decrypt_record

# Blockchain imports
from web3 import Web3
import pickle

app = Flask(__name__)
CORS(app)

# -----------------------------
# Files
# -----------------------------
USERS_FILE = "users.json"
METRICS_FILE = "metrics/metrics_log.jsonl"
os.makedirs("metrics", exist_ok=True)

# -----------------------------
# Helper: Password Hashing
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------------
# Blockchain Setup
# -----------------------------
GANACHE_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
account = w3.eth.accounts[0]

with open("contract_abi.json") as f:
    abi = json.load(f)

with open("contract_addr.txt") as f:
    contract_address = f.read().strip()

contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

# -----------------------------
# Metrics Logger
# -----------------------------
def log_metric(entry):
    with open(METRICS_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

# =====================================================
# REGISTER API
# =====================================================
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data["email"]
    password = hash_password(data["password"])
    role = data["role"]

    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            users = json.load(f)

    if email in users:
        return jsonify({"status": "FAIL", "message": "User already exists"})

    users[email] = {
        "password": password,
        "role": role
    }

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

    return jsonify({"status": "OK", "message": "Registration successful"})

# =====================================================
# LOGIN API
# =====================================================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = hash_password(data["password"])

    if not os.path.exists(USERS_FILE):
        return jsonify({"status": "FAIL"})

    with open(USERS_FILE) as f:
        users = json.load(f)

    if email in users and users[email]["password"] == password:
        return jsonify({
            "status": "OK",
            "role": users[email]["role"]
        })

    return jsonify({"status": "FAIL"})

# =====================================================
# SEARCH API
# =====================================================
@app.route("/search", methods=["POST"])
def search():
    data = request.json
    keyword = data["keyword"]

    start = time.time()
    records = search_records(keyword)
    end = time.time()

    #log_metric({
    #    "module": "Search API",
     #   "keyword": keyword,
      #  "results": len(records),
       # "time_ms": round((end - start) * 1000, 3)
    #})

    return jsonify(records)

# =====================================================
# ACCESS REQUEST API
# =====================================================
@app.route("/request-access", methods=["POST"])
def request_access():
    data = request.json

    record_id = data["record_id"]
    role = data["role"]
    emergency = data["emergency"]

    print("\nACCESS REQUEST")
    print("Record     :", record_id)
    print("Role       :", role)
    print("Emergency  :", emergency)

    # --------------------------------------------------
    # 1. Ask blockchain_access module (RBAC + ABAC)
    # --------------------------------------------------
    cid = request_access_from_blockchain(
        contract, record_id, role, emergency, account
    )

    print("ACCESS GRANTED for record:", record_id)
    print("CID fetched:", cid)
    print("Fetching encrypted data from IPFS...")

    data = retrieve_and_decrypt_record(cid)
    print("Decryption completed")
    print("Decrypted values:", data)

    return jsonify({
        "status": "ALLOWED",
        "data": data
    })



    



# =====================================================
# RUN APP
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)
