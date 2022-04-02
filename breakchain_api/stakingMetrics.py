from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import environ
import os
ROOT_DIR = os.path.abspath(os.curdir) + "/breakchain_api/"
env = environ.Env()
environ.Env.read_env()


def get_staking_metrics():
    w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.matic.today'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    with open(ROOT_DIR + "abi/xchain_abi.json") as f:
        xchain_abi = json.load(f)

    xchain = w3.eth.contract(address=env("XCHAIN_ADDRESS"), abi=xchain_abi)

    totalSupplyXchain = (xchain.functions.totalSupply().call()) * (10 ** 9)
    stakingAddress = env("STAKING_ADDRESS")
    stakedXchain = (xchain.functions.balanceOf(stakingAddress).call()) * 10 ** 9

    # APY and ROI 5 Day
    distributed = (totalSupplyXchain / 10 ** 18) * .003
    rewardYield = distributed / (stakedXchain / 10 ** 18)
    apy = ((1 + rewardYield / 100) ** (3 * 365) - 1) * 100
    roi5 = ((1 + rewardYield / 100) ** (3 * 5) - 1) * 100

    # Total Value Locked
    with open(ROOT_DIR + "abi/usdc_abi.json") as f:
        usdc_abi = json.load(f)
    usdc = w3.eth.contract(address=env("USDC_ADDRESS"), abi=usdc_abi)
    treasuryAddress = env("TREASURY_ADDRESS")
    treasuryUSDCbalance = usdc.functions.balanceOf(treasuryAddress).call()
    priceFloor = (treasuryUSDCbalance / totalSupplyXchain)

    tvl = priceFloor * (stakedXchain / 10 ** 18)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "APY": apy,
                "ROI-5-Day": roi5,
                "total-locked-value": tvl,
                "xchain-price": priceFloor,
                "next-reward-amount": "",
                "next-reward-yield": "",
                "your-earnings-per-day": "",
                "position": ""
            }

        )
    }

