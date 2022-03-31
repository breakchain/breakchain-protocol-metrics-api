from web3 import Web3
from web3.middleware import geth_poa_middleware
import json


def dashboardMetrics():

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

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "xchain-price": "",
                "market-cap": "",
                "price-floor": priceFloor,
                "xchain-staked": stakedRatio,
                "circulating-supply": circulatingSupply,
                "runway-available": "",
                "total-value-locked": tvl,
                "treasury-assets": treasuryAssets,
                "treasury-backing": treasuryAssets
            }

        )
    }


def stakingMetrics():
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


'''
def bondMetrics():

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "metric1": 1,
                "metric2": 2
            }

        )
    }


w3 = Web3(Web3.HTTPProvider(
    'https://rpc-mumbai.matic.today'))

w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# print(w3.isConnected())
# print(w3.eth.get_block('latest'))
# print(w3.eth.get_balance('0xb3434bF68203676366FBf0C42347B394B7203fB4'))
# prints matic balance

user_address = "0xb3434bF68203676366FBf0C42347B394B7203fB4"

# Get User XCHAIN Balance
with open("xchain_abi.json") as f:
    xchain_abi = json.load(f)

xchain = w3.eth.contract(
    address='0xd3d2d5F7582b53F0929D06fB6f12473811ba2aB5', abi=xchain_abi)

userXchainBalance = xchain.functions.balanceOf(user_address).call()
print("XCHAIN Balance: " + str(userXchainBalance / 10**9))

# Get User sXCHAIN Balance
with open("sxchain_abi.json") as f:
    sxchain_abi = json.load(f)

sxchain = w3.eth.contract(
    address='0xBB3A0712AA17cE116358d71F6C07EB4505D7910a', abi=sxchain_abi)

user_sXchainBalance = sxchain.functions.balanceOf(user_address).call()
print("sXCHAIN Balance: " + str(user_sXchainBalance / 10**9))

# PRICE FLOOR (Total supply XCHAIN / value of reserves)

totalSupplyXchain = (xchain.functions.totalSupply().call())*(10**9)

with open("usdc_abi.json") as f:
    usdc_abi = json.load(f)

usdc = w3.eth.contract(
    address='0x9a7E7639322643d02F8CB478baB0EB1019F82389', abi=usdc_abi)

treasuryAddress = "0x08BC282d0970b19c7E86E6fa35693e321F9E5B50"
treasuryUSDCbalance = usdc.functions.balanceOf(treasuryAddress).call()
# print(totalSupplyXchain*10**9)
# print(treasuryUSDCbalance)
priceFloor = (treasuryUSDCbalance / totalSupplyXchain)
print("Price Floor in USD: " + str(priceFloor))

# XCHAIN STAKED % (STAKED / TOTAL SUPPLY) (STAKED == XCHAIN balance of the STAKING contract)

stakingAddress = "0x033976e7f7c4FEfa3310Ff29DBe46Fc41329a62A"
stakedXchain = (xchain.functions.balanceOf(stakingAddress).call())*10**9

print("Staked Ratio Percentage: " + str(stakedXchain/totalSupplyXchain*100))

# Circulating Supply

print("Circulating Supply Quantity: " + str(totalSupplyXchain/10**18))

# Treasury Assets (reserve balance of treasury)

print("Treasury Assets in USD: " + str(treasuryUSDCbalance/10**18))

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

# Staking APY

# Amount staked * (1+ reward rate per epoch)^ amount of epochs.
#apy = (1+(.4059*.01))**1095
# found on reddit -- not verified

# from ohm docs
distributed = (totalSupplyXchain/10**18) * .003
# print(distributed)
rewardYield = distributed / (stakedXchain/10**18)
# print(rewardYield)
apy = ((1+rewardYield/100)**(3*365)-1)*100
print("APY: " + str(apy))

print("5 Day Rate: " + str(((1+rewardYield/100)**(3*5)-1)*100))


'''
'''
#temaplte
quickswapPairAddress = ""

with open("quickswap_abi.json") as f:
    quickswap_abi = json.load(f)

quickswap = w3.eth.contract(
    address=quickswapPairAddress, abi=quickswap_abi)

quickswapReserves = quickswap.functions.getReserves().call()

marketPrice = quickswapReserves[0] / quickswapReserves[1]

print("XCHAIN Market Price in USD: " + str(marketPrice))
print("Market Cap: " + str(marketPrice*(totalSupplyXchain/10**18)))
print("Total Value Locked: " + str(marketPrice*(stakedXchain/10**18)))
'''

'''

# using mainnet
w3 = Web3(Web3.HTTPProvider(
    'https://polygon-rpc.com'))

w3.middleware_onion.inject(geth_poa_middleware, layer=0)

quickswapPairAddress = "0x74214F5d8AA71b8dc921D8A963a1Ba3605050781"

with open("quickswap_abi.json") as f:
    quickswap_abi = json.load(f)

quickswap = w3.eth.contract(
    address=quickswapPairAddress, abi=quickswap_abi)

quickswapReserves = quickswap.functions.getReserves().call()

marketPrice = quickswapReserves[0] / quickswapReserves[1]

# print(quickswapReserves[0])
# print(quickswapReserves[1])

# XCHAIN Market Price (Market from Quickswap)
# Market Cap (TOTALY SUPPLY * market price)
# TOTAL VALUE LOCKED (# of xchain staked * market price)

print("XCHAIN Market Price in USD: " + str(marketPrice))
print("Market Cap in USD: " + str(marketPrice*(totalSupplyXchain/10**18)))
print("Total Value Locked in USD: " + str(marketPrice*(stakedXchain/10**18)))


# Bond Discount

bondDiscount = (marketPrice - bondPrice) / marketPrice
print("Bond Discount is: " + str(bondDiscount))


# Runway Available (not sure)
'''
