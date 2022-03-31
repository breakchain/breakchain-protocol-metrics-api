from web3 import Web3
from web3.middleware import geth_poa_middleware
import json


def bondMetrics(event, context):

    w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.matic.today'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Bond Price

    with open("usdcbond_abi.json") as f:
        usdcbond_abi = json.load(f)

    usdcbond = w3.eth.contract(
        address='0x95e9BA3E289888ACd402c3c7b88B2356592b0C59', abi=usdcbond_abi)

    bondPrice = usdcbond.functions.bondPriceInUSD().call() / 10**18

    print("Bond Price: " + str(bondPrice))

    # Debt Ratio
    debtRatio = usdcbond.functions.debtRatio().call() / 100
    print("Debt Ratio: " + str(debtRatio))

    with open("xchain_abi.json") as f:
        xchain_abi = json.load(f)

    # Temp ROI. Change to market price in the future
    xchain = w3.eth.contract(
        address='0xd3d2d5F7582b53F0929D06fB6f12473811ba2aB5', abi=xchain_abi)

    totalSupplyXchain = (xchain.functions.totalSupply().call())*(10**9)
    with open("usdc_abi.json") as f:
        usdc_abi = json.load(f)
    usdc = w3.eth.contract(
        address='0x9a7E7639322643d02F8CB478baB0EB1019F82389', abi=usdc_abi)
    treasuryAddress = "0x08BC282d0970b19c7E86E6fa35693e321F9E5B50"
    treasuryUSDCbalance = usdc.functions.balanceOf(treasuryAddress).call()
    priceFloor = (treasuryUSDCbalance / totalSupplyXchain)

    roi = (priceFloor - bondPrice) / priceFloor

    # max price

    maxPrice = usdcbond.functions.maxPayout().call() / 10**9

    # You will get == (amount deposited / bond price)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "you-will-get": "",
                "max-you-can-buy": maxPrice,
                "ROI": roi,
                "debt-ratio": debtRatio,
                "vesting-term": "5 Days"

            }

        )
    }


print(bondMetrics("event", "context"))
