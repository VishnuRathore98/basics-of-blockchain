# This script deploys a smart contract to solidity compatible ganache blockchain.

# solcx is a Python wrapper for the Solidity compiler (solc)
# Needed to turn Solidity code into bytecode
from solcx import compile_standard, install_solc
from solcx.exceptions import SolcNotInstalled

from dotenv import load_dotenv
from pprint import pprint

# Web3.py lets Python interact with Ethereum blockchains
# Used to send transactions, deploy contracts, call functions
from web3 import Web3
import json
import os


load_dotenv()

# Loads your Solidity contract into memory
with open(file="./SimpleStorage.sol", mode="r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)


try:
    # Compile the Solidity Contract
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
    # print(compiled_sol)
    with open("./compiled_sol.json", "w") as file:
        json.dump(compiled_sol, file)

    # Deployed to the blockchain
    bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
        "bytecode"
    ]["object"]
    # print("Bytecode: ", bytecode)

    # Used by Web3 to call contract functions
    abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
    # print("ABI: ", abi)

    # Connecting to ganache
    # Ganache simulates Ethereum for development
    w3 = Web3(provider=Web3.HTTPProvider(endpoint_uri=os.environ.get("ENDPOINT_URI")))

    # Chain ID prevents replay attacks
    chain_id = 11155111

    # The address will send the deployment transaction
    my_address = os.environ.get("MY_ADDRESS")

    # The private key signs the transaction
    private_key = os.environ.get("PRIVATE_KEY")

    # Create the contract object
    # This does not deploy the contract yet.
    # It just tells Web3:
    # “Here’s what the contract looks like and how to deploy it.”
    SimpleStorage = w3.eth.contract(bytecode=bytecode, abi=abi)

    # Get the Nonce (Transaction Counter)
    # Each transaction from an account must have a unique nonce
    # Prevents duplicate or replayed transactions
    nonce = w3.eth.get_transaction_count(account=my_address)

    # Building the Deployment Transaction

    print("Deploying contract...")

    # 1. Build a transanction
    transaction = SimpleStorage.constructor().build_transaction(
        {"chainId": chain_id, "from": my_address, "nonce": nonce}
    )
    # print("1. Transaction built: ", transaction)

    # 2. Sign a transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    # print("2. Transactin signed: ", signed_txn)

    # 3. Send a transaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    # print("3. Transaction sent: ", tx_hash)

    # this will stop the code until the transaction hash is gone through
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    # print("4. Trasaction receipt: ", tx_receipt)

    print("Contract deployed!")

    # Updating contract

    print("Updating contract...")

    # Bind to Deployed Contract
    simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

    # Build store(10) Transaction
    store_transaction = simple_storage.functions.store(10).build_transaction(
        {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
    )

    # Sign Transaction
    signed_store_txn = w3.eth.account.sign_transaction(
        store_transaction, private_key=private_key
    )

    # Send and update Transaction state
    send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.raw_transaction)

    # Wait for Transaction receipt
    store_tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

    print("Contract Updated!")

    # Read Transaction state
    print(simple_storage.functions.retrieve().call())

    print("Transaction completed!")
except SolcNotInstalled:
    print("Solc Installing ...")
    install_solc("0.8.0")
