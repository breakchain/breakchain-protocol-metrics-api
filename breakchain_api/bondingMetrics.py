from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import environ
import os
ROOT_DIR = os.path.abspath(os.curdir) + "/breakchain_api/"
env = environ.Env()
environ.Env.read_env()


def get_bonding_metrics():

    w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.matic.today'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Bond Price

    with open(ROOT_DIR + "abi/usdcbond_abi.json") as f:
        usdcbond_abi = json.load(f)

    usdcbond = w3.eth.contract(env("USDC_BOND_ADDRESS"), abi=usdcbond_abi)

    bondPrice = usdcbond.functions.bondPriceInUSD().call() / 10**18

    print("Bond Price: " + str(bondPrice))

    # Debt Ratio
    debtRatio = usdcbond.functions.debtRatio().call() / 100
    print("Debt Ratio: " + str(debtRatio))

    with open(ROOT_DIR + "abi/xchain_abi.json") as f:
        xchain_abi = json.load(f)

    # Temp ROI. Change to market price in the future
    xchain = w3.eth.contract(address=env("XCHAIN_ADDRESS"), abi=xchain_abi)

    totalSupplyXchain = (xchain.functions.totalSupply().call())*(10**9)
    with open(ROOT_DIR + "abi/usdc_abi.json") as f:
        usdc_abi = json.load(f)
    usdc = w3.eth.contract(address=env("USDC_ADDRESS"), abi=usdc_abi)
    treasuryAddress = env("TREASURY_ADDRESS")
    treasuryUSDCbalance = usdc.functions.balanceOf(treasuryAddress).call()
    priceFloor = (treasuryUSDCbalance / totalSupplyXchain)

    roi = (priceFloor - bondPrice) / priceFloor

    # max price

    maxPrice = usdcbond.functions.maxPayout().call() / 10**9

    # You will get == (amount deposited / bond price)

    return {
        "statusCode": 200,
        "body": {
            "you-will-get": "",
            "max-you-can-buy": maxPrice,
            "ROI": roi,
            "debt-ratio": debtRatio,
            "vesting-term": "5 Days"
        }
    }

