from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import numpy as np
import environ
import os
ROOT_DIR = os.path.abspath(os.curdir) + "/breakchain_api/"
env = environ.Env()
environ.Env.read_env()


def get_dashboard_metrics():
    w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.matic.today'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    with open(ROOT_DIR + "abi/xchain_abi.json") as f:
        xchain_abi = json.load(f)
    print(env("XCHAIN_ADDRESS"))

    xchain = w3.eth.contract(address=env("XCHAIN_ADDRESS"), abi=xchain_abi)

    # PRICE FLOOR
    totalSupplyXchain = (xchain.functions.totalSupply().call())*(10**9)
    with open(ROOT_DIR + "abi/usdc_abi.json") as f:
        usdc_abi = json.load(f)

    usdc = w3.eth.contract(address=env("USDC_ADDRESS"), abi=usdc_abi)

    treasuryAddress = env("TREASURY_ADDRESS")
    treasuryUSDCbalance = usdc.functions.balanceOf(treasuryAddress).call()

    priceFloor = (treasuryUSDCbalance / totalSupplyXchain)

    # XCHAIN STAKED %
    stakingAddress = env("STAKING_ADDRESS")
    stakedXchain = (xchain.functions.balanceOf(stakingAddress).call())*10**9

    stakedRatio = stakedXchain/totalSupplyXchain*100

    # Circulating Supply
    circulatingSupply = totalSupplyXchain/10**18

    # Treasury Assets (reserve balance of treasury)
    treasuryAssets = treasuryUSDCbalance/10**18

    #  Total Value Locked (can switch to market price)
    tvl = priceFloor*(stakedXchain/10**18)

    # APY and ROI 5 Day
    distributed = (totalSupplyXchain/10**18) * .003
    rewardYield = distributed / (stakedXchain/10**18)

    # runway
    rfv = treasuryAssets
    runway = (np.log(rfv/(stakedXchain/10**18)) /
              np.log(1+(rewardYield/100)))/3

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "xchain-price": priceFloor,
                "market-cap": priceFloor*circulatingSupply,
                "price-floor": priceFloor,
                "xchain-staked": stakedRatio,
                "circulating-supply": circulatingSupply,
                "runway-available": runway,
                "total-value-locked": tvl,
                "treasury-assets": treasuryAssets,
                "treasury-backing": treasuryAssets
            }

        )
    }