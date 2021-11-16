from brownie import accounts, Lottery, config, network
from scripts.helper_functions import fund_with_link, get_accounts, get_contracts
import time


def deploy_lottery():
    account = get_accounts()
    Lottery.deploy(get_contracts("eth_usd_price_address").address, 
        get_contracts("vrf_coordinator").address, 
        get_contracts("link_token").address, 
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False))


def start_lottery():
    account = get_accounts()
    lottery = Lottery[-1]
    start_lottery = lottery.startLottery({"from": account})
    start_lottery.wait(1)
    print("Start lottery")


def enter_lottery():
    account = get_accounts()
    lottery = Lottery[-1]
    value = lottery.getEnteranceFee() + 10000000
    tx = lottery.enterLottery({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery")


def end_lottery():
    account = get_accounts()
    lottery = Lottery[-1]
    funding = fund_with_link(lottery.address)
    funding.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(60)

    print(f'{lottery.recentWinner} is the winner')
    # We need to fund the contarct with some link
def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
