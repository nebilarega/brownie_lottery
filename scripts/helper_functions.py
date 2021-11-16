from brownie import config, accounts, Lottery, network, MockV3Aggregator, Contract, VRFCoordinatorMock, LinkToken


FORKED_LOCAL_ENVIROMENTS = ["mainnet-fork-dev", "mainnet-fork"]
LOCAL_ACCOUNT_ARRAY = ["development", "ganache-local"]


def get_accounts(index=None, ID=None):
    if index:
        return accounts[index]
    if ID:
        return accounts.load(ID)
    if network.show_active() in LOCAL_ACCOUNT_ARRAY or network.show_active() in FORKED_LOCAL_ENVIROMENTS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])
contract_to_mock = {
    "eth_usd_price_address": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}

def get_contracts(contract_name):
     """
     This function will grab the contract addresses from brownie if defined or 
     deploy mock version of the contracts and return that contract
     Args:
        contract_name: string
     Returns:
        brownie.network.contract.ProjectContract: Most recently version of the deployed contract
     """
     contract_type = contract_to_mock[contract_name]
     if network.show_active() in LOCAL_ACCOUNT_ARRAY:
         if len(contract_type) <= 0:
             deploy_mocks()
         contract = contract_type[-1]
     else:
         contract_address = config["networks"][network.show_active()][contract_name]
         # We create a contract using the ABI and the address
         contract = Contract(contract_type._name, contract_address, contract_type.abi)
     return contract

DECIMALS = 8
INITIAL_VALUE = 200000000000
def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_accounts()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})


def fund_with_link(contract_address, account=None, link_token=None, amount=1000000000000000000):
    account = account if account else get_accounts()
    link_token = link_token if link_token else get_contracts("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print(f"Funded {contract_address} with {amount/10**18} LINK")
    return tx