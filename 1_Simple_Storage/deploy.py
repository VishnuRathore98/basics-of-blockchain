from web3 import Web3
from solcx import compile_standard, install_solc
from solcx.exceptions import SolcNotInstalled
from dotenv import load_dotenv
from pprint import pprint
import os

load_dotenv()


with open(file="./SimpleStorage.sol", mode="r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)


try:
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                }
            },
        },
        solc_version="0.8.0",
    )
    print(compiled_sol)

except SolcNotInstalled:
    print("Solc Installing ...")
    install_solc("0.8.0")
