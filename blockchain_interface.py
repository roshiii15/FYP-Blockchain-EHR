from web3 import Web3
import json

GANACHE_URL = "http://127.0.0.1:7545"
CONTRACT_ADDRESS = "0xa3309c157B2EC4F1500b0FdE111600468650013c"

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
assert w3.isConnected()

with open("contract_abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(
    address=Web3.toChecksumAddress(CONTRACT_ADDRESS),
    abi=abi
)

DEFAULT_ACCOUNT = w3.eth.accounts[0]
w3.eth.default_account = DEFAULT_ACCOUNT
