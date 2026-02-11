from dotenv import load_dotenv
from pprint import pprint
import os
from brownie import accounts, config, SimpleStorage


load_dotenv()


def deploy_simple_storage():
    account = accounts[0]
    simple_storage = SimpleStorage.deploy({"from": account})
    stored_value = simple_storage.retrieve()
    print("stored value: ", stored_value)
    transaction = simple_storage.store(10, {"from": account})
    transaction.wait(1)
    updated_stored_value = simple_storage.retrieve()
    print("updated value: ", updated_stored_value)


def main():
    deploy_simple_storage()
