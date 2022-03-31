from web3 import Web3
from web3.middleware import geth_poa_middleware
import json


def stakingMetrics(event, context):
    w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.matic.today'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    with open("xchain_abi.json") as f:
        xchain_abi = json.load(f)

    xchain = w3.eth.contract(
        address='0xd3d2d5F7582b53F0929D06fB6f12473811ba2aB5', abi=xchain_abi)

    totalSupplyXchain = (xchain.functions.totalSupply().call())*(10**9)
    stakingAddress = "0x033976e7f7c4FEfa3310Ff29DBe46Fc41329a62A"
    stakedXchain = (xchain.functions.balanceOf(stakingAddress).call())*10**9

    # APY and ROI 5 Day
    distributed = (totalSupplyXchain/10**18) * .003
    rewardYield = distributed / (stakedXchain/10**18)
    apy = ((1+rewardYield/100)**(3*365)-1)*100
    roi5 = ((1+rewardYield/100)**(3*5)-1)*100

    # Total Value Locked
    with open("usdc_abi.json") as f:
        usdc_abi = json.load(f)
    usdc = w3.eth.contract(
        address='0x9a7E7639322643d02F8CB478baB0EB1019F82389', abi=usdc_abi)
    treasuryAddress = "0x08BC282d0970b19c7E86E6fa35693e321F9E5B50"
    treasuryUSDCbalance = usdc.functions.balanceOf(treasuryAddress).call()
    priceFloor = (treasuryUSDCbalance / totalSupplyXchain)

    tvl = priceFloor*(stakedXchain/10**18)

    # next reward amount == reward yield * principal
    # your earnings per day == ((APY*principal) +principal) / 365
    # remove position

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "APY": apy,
                "ROI-5-Day": roi5,
                "total-locked-value": tvl,
                "xchain-price": priceFloor,
                "next-reward-amount": "",
                "next-reward-yield": rewardYield,
                "your-earnings-per-day": "",
                "position": ""
            }

        )
    }


print(stakingMetrics("event", "context"))
