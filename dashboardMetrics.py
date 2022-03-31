from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import numpy as np


def dashboardMetrics(event, context):

    w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.matic.today'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    with open("xchain_abi.json") as f:
        xchain_abi = json.load(f)

    xchain = w3.eth.contract(
        address='0xd3d2d5F7582b53F0929D06fB6f12473811ba2aB5', abi=xchain_abi)

    # PRICE FLOOR
    totalSupplyXchain = (xchain.functions.totalSupply().call())*(10**9)

    with open("usdc_abi.json") as f:
        usdc_abi = json.load(f)

    usdc = w3.eth.contract(
        address='0x9a7E7639322643d02F8CB478baB0EB1019F82389', abi=usdc_abi)

    treasuryAddress = "0x08BC282d0970b19c7E86E6fa35693e321F9E5B50"
    treasuryUSDCbalance = usdc.functions.balanceOf(treasuryAddress).call()

    priceFloor = (treasuryUSDCbalance / totalSupplyXchain)

    # XCHAIN STAKED %
    stakingAddress = "0x033976e7f7c4FEfa3310Ff29DBe46Fc41329a62A"
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


print(dashboardMetrics("event", "context"))
