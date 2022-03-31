from web3 import Web3
from web3.middleware import geth_poa_middleware
import json


def bondMetrics(event, context):

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

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "metric1": 1,
                "metric2": 2
            }

        )
    }


print(bondMetrics())
