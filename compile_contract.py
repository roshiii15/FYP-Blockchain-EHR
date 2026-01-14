from solcx import compile_standard, install_solc
import json

install_solc("0.8.17")

with open("HealthcareAccess.sol", "r") as f:
    source = f.read()

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "HealthcareAccess.sol": {"content": source}
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        },
    },
    solc_version="0.8.17"
)

contract_data = compiled["contracts"]["HealthcareAccess.sol"]["HealthcareAccess"]

with open("contract_abi.json", "w") as f:
    json.dump(contract_data["abi"], f)

with open("contract_bytecode.txt", "w") as f:
    f.write(contract_data["evm"]["bytecode"]["object"])

print("Contract compiled with Solidity 0.8.17")
