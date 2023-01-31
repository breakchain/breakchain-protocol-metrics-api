from web3 import Web3
from requests import Session
from web3.middleware import geth_poa_middleware
import json
import numpy as np
import environ
import os
ROOT_DIR = os.path.abspath(os.curdir) + "/breakchain_api/"
env = environ.Env()
environ.Env.read_env()


def get_dashboard_metrics():
    w3 = Web3(Web3.HTTPProvider(
        'https://polygon-mainnet.infura.io/v3/18c3956af9734c289bfed9eee03ee1a7'))
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
    ust = w3.eth.contract(address=env("UST_ADDRESS"), abi=usdc_abi)

    treasuryAddress = env("TREASURY_ADDRESS")
    treasuryUSDCbalance = usdc.functions.balanceOf(treasuryAddress).call()
    treasuryUSTbalance = ust.functions.balanceOf(treasuryAddress).call()
    '''
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {'slug': 'terrausd', 'convert': 'USD'}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'c5c8af8c-8412-4f9d-b75d-77119896d3e4'
    }  
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    info = json.loads(response.text)

    ustPrice = info['data']['7129']['quote']['USD']['price']
    '''
    # new ust market price
    with open(ROOT_DIR + "abi/quickswap_abi.json") as f:
        quickswap_abi = json.load(f)

    quickswap = w3.eth.contract(
        address="0xc5fB609D8aE6e4dEB4be844AFB6DF86874B49d9D", abi=quickswap_abi)

    quickswapReserves = quickswap.functions.getReserves().call()

    ustPrice = (quickswapReserves[0]) / (quickswapReserves[1])
    # end

    treasuryBalance = treasuryUSDCbalance + (ustPrice*treasuryUSTbalance)

    priceFloor = (treasuryBalance*10**12 / totalSupplyXchain)

    # Market Price
    with open(ROOT_DIR + "abi/quickswap_abi.json") as f:
        quickswap_abi = json.load(f)

    quickswap = w3.eth.contract(
        address="0xbE919AEE42b9CFD94B3d237AaC6EcDE1826a04d3", abi=quickswap_abi)

    quickswapReserves = quickswap.functions.getReserves().call()

    marketPrice = (quickswapReserves[1]/10**6) / (quickswapReserves[0]/10**9)

    # XCHAIN STAKED %
    stakingAddress = env("STAKING_ADDRESS")
    stakedXchain = (xchain.functions.balanceOf(stakingAddress).call())*10**9

    stakedRatio = stakedXchain/totalSupplyXchain*100

    # Circulating Supply
    circulatingSupply = totalSupplyXchain/10**18

    # Treasury Assets (reserve balance of treasury)
    treasuryAssets = treasuryBalance/10**6

    #  Total Value Locked (can switch to market price)
    tvl = marketPrice*(stakedXchain/10**18)

    # APY and ROI 5 Day
    distributed = (totalSupplyXchain/10**18) * .07
    rewardYield = 0
    if stakedXchain != 0:
        rewardYield = distributed / (stakedXchain / 10 ** 18)

    # runway
    rfv = treasuryAssets
    runway = 0
    if stakedXchain != 0 and rfv != 0:
        runway = (np.log(rfv/(stakedXchain/10**18)) /
                  np.log(1+(rewardYield/100)))/3
    print(runway)

    # apy
    apy = ((1 + rewardYield / 100) ** (3 * 365) - 1) * 100
    apy1day = ((1 + rewardYield / 100) ** (3) - 1) * 100
    roi5 = ((1 + rewardYield / 100) ** (3 * 5) - 1) * 100

    # bond
    with open(ROOT_DIR + "abi/usdcbond_abi.json") as f:
        usdcbond_abi = json.load(f)

    usdcbond = w3.eth.contract(env("USDC_BOND_ADDRESS"), abi=usdcbond_abi)
    bondPrice = usdcbond.functions.bondPriceInUSD().call() / 10 ** 6
    maxPrice = usdcbond.functions.maxPayout().call() / 10 ** 9
    roi = ((marketPrice - bondPrice) / marketPrice) * 100
    # Debt Ratio
    debtRatio = usdcbond.functions.debtRatio().call() / 100
    print("Debt Ratio: " + str(debtRatio))

    return {
        "statusCode": 200,
        "body": {
            "xchain-price": marketPrice,
            "market-cap": marketPrice*circulatingSupply,
            "price-floor": priceFloor,
            "xchain-staked": stakedRatio,
            "circulating-supply": circulatingSupply,
            "runway-available": runway,
            "total-value-locked": tvl,
            "treasury-assets": treasuryAssets,
            "treasury-backing": treasuryAssets,
            "APY": apy,
            "ROI-5-Day": roi5,
            "APY-1-Day": apy1day,
            "total-locked-value": tvl,
            "next-reward-amount": "",
            "next-reward-yield": rewardYield,
            "your-earnings-per-day": "",
            "position": "",
            "you-will-get": "",
            "bond-price": bondPrice,
            "max-you-can-buy": maxPrice,
            "ROI": roi,
            "debt-ratio": debtRatio,
            "vesting-term": "15 Days"
        }
    }
