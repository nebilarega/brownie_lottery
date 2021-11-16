from brownie import config, accounts, Lottery, network
from scripts.helper_functions import get_accounts
from web3 import Web3

def test_get_enterance_fee():
    account = accounts[0]
    lottery = Lottery.deploy(config["networks"][network.show_active()]["eth_usd_price_address"], {"from": account})
    
    assert lottery.getEnteranceFee() > Web3.toWei(0.010, "ether")

