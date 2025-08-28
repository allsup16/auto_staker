from pathlib import Path
from datetime import time
import http.client
import json
import numpy as np
import uuid

LOG_PATH = Path("log.json")


########### Interact with coinbase ##################### 
def Total(client,accounts):
    products = ''
    total = 0 #total seems to miss staked ETH
    amount = 0
    for x in accounts.accounts:
        if x.name == 'Cash (USD)' or x.name == 'USDC Wallet':
            amount= np.float64(x.available_balance['value'])
        elif np.float64(x.available_balance['value'])>0:
            products = client.get_product(f"{x.currency}-USD")
            amount=np.round(np.float64(products.price),decimals=0)*np.float64(x.available_balance['value'])
        total+=amount
    return np.round(total,decimals=2)
def MyBTCAccount(accounts):
    for x in accounts.accounts:
        if x.name == 'BTC Wallet':
            return x
    return 'Account not found'    
def MyBTCValue(client,accounts):
    amount=0
    for x in accounts.accounts:
        if x.name == 'BTC Wallet':
            product = client.get_product(f"{x.currency}-USD")
            amount=np.round(np.float64(product.price),decimals=0)*np.float64(x.available_balance['value'])
    return amount    
def MyUSDCValue(accounts):
    amount=0
    for x in accounts.accounts:
        if x.name == 'USDC Wallet':
            amount= np.float64(x.available_balance['value'])
    return amount    
def BTCValue(client):
    return np.float64(client.get_product("BTC-USD")['price'])
def OrderInfo(client,orderId):
    return client.get_order(orderId)
def BuyBTC(client, seed): 
    print('Placing Buy Order...')
    try:
        order = client.market_order_buy(
            client_order_id=str(uuid.uuid4()), 
            product_id="BTC-USDC", 
            quote_size=f"{seed:.8f}"  # buying $seed worth of BTC
        )
        print('Buy order placed:', order)
        return order
    except Exception as e:
        print("Buy failed:", e)
        return None
def SellBTCLimit(client,orderInfo,SeedSellThresh,PercentToSell):
    try: 
        clientId = str(uuid.uuid4())
        productId = orderInfo['order']['product_id']
        filledSize = float(orderInfo['order']['filled_size'])
        boughtPrice = float(orderInfo['order']['average_filled_price'])
        targetSalePrice = boughtPrice + boughtPrice * (SeedSellThresh / 100)
        filledSize = filledSize * (PercentToSell/100)
        limit_price = f"{targetSalePrice:.2f}"
        base_size = f"{filledSize:.8f}"
        order = client.limit_order_gtc_sell(
            client_order_id=clientId,
            product_id=productId,
            base_size=base_size,
            limit_price=limit_price,
            post_only=True)
        return order
    except Exception as e:
        print("Sell failed:", e)
        return None
def month_spread(client,granularity="ONE_DAY",days_back=30):
        seconds=86400#seconds in a day
        now = client.get_unix_time()
        end_ts = int(now["epoch_seconds"])
        start_ts = end_ts - (days_back * seconds)  # 30 days ago
        product = client.get_candles("BTC-USD", start=start_ts, end=end_ts, granularity=granularity)
        high=0
        price=float(client.get_product("BTC-USD")['price'])
        low = float('inf')
        for days in product['candles']:
            if float(days['low'])<low:
                low = float(days['low'])
            if float(days['high'])>high:
                high = float(days['high'])
        return price,low,high




######### Handles json files #####################
def Dynamic_update(client,general_instructions):
    Granularity = general_instructions['General_Instructions']['Candles']['Granularity']
    DaysBack = general_instructions['General_Instructions']['Candles']['Days_Back']
    price,low,high=month_spread(client,Granularity,DaysBack)
    print("Price: ",price)
    print("Low: ",low)
    print("High: ",high)
    #Current State
    ShortState = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['State']
    LongState = general_instructions['General_Instructions']['Dynamic_Adjustment_Long']['State']
    general_instructions = Update(general_instructions,price,'Dynamic_Adjustment_Short',low,high,ShortState)
    general_instructions = Update(general_instructions,price,'Dynamic_Adjustment_Long',low,high,LongState)
    WriteInstructions("general_instructions",general_instructions)
    return LoadInstructions("general_instructions")

def Update(general_instructions,price,Dynamic_Adjustment,low,high,State):
    #Modify State
    PercentLow = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_Low']
    PercentHigh = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_High']
    PercentMediumLow = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_Medium_Low']
    PercentMediumHigh = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_Medium_High']

    #Modify triggers in the State
    LowPercentChangeTrigger = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_Low_Change_Trigger']
    HighPercentChangeTrigger = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_High_Change_Trigger']
    MediumLowPercentChangeTrigger = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_Medium_Low_Change_Trigger']
    MediumHighPercentChangeTrigger = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_Medium_High_Change_Trigger']
    DefaultTrigger = general_instructions['General_Instructions'][Dynamic_Adjustment]['Trigger_Default']

    #Modify amount to used in each purchase
    LowSeedSize = general_instructions['General_Instructions'][Dynamic_Adjustment]['Seed_Size_Low']
    HighSeedSize = general_instructions['General_Instructions'][Dynamic_Adjustment]['Seed_Size_High']
    MediumLowSeedSize = general_instructions['General_Instructions'][Dynamic_Adjustment]['Seed_Size_Medium_Low']
    MediumHighSeedSize = general_instructions['General_Instructions'][Dynamic_Adjustment]['Seed_Size_Medium_High']
    DefaultSeedSize = general_instructions['General_Instructions'][Dynamic_Adjustment]['Seed_Size_Default']

    #Modify Threshold amounts (How much price must increase to sell)
    LowSellThreshHold = general_instructions['General_Instructions'][Dynamic_Adjustment]['Sell_Threshold_Percentage_Low']
    HighSellThreshHold = general_instructions['General_Instructions'][Dynamic_Adjustment]['Sell_Threshold_Percentage_High']
    MediumLowSellThreshHold = general_instructions['General_Instructions'][Dynamic_Adjustment]['Sell_Threshold_Percentage_Medium_Low']
    MediumHighSellThreshHold = general_instructions['General_Instructions'][Dynamic_Adjustment]['Sell_Threshold_Percentage_Medium_High']
    DefaultSellThreshHold = general_instructions['General_Instructions'][Dynamic_Adjustment]['Sell_Threshold_Percentage_Default']

    #Modify percentage of amount of purchase that is sold
    LowPercentToBeSold = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_To_Be_Sold_Low']
    HighPercentToBeSold = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_To_Be_Sold_High']
    MediumLowPercentToBeSold = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_To_Be_Sold_Medium_Low']
    MediumHighPercentToBeSold = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_To_Be_Sold_Medium_High']
    DefaultPercentToBeSold = general_instructions['General_Instructions'][Dynamic_Adjustment]['Percent_To_Be_Sold_Default']

    #Modify the funds that are manditory to be kept in USDC
    LowMinimumReqiured = general_instructions['General_Instructions'][Dynamic_Adjustment]['Minimum_Required_Low']
    HighMinimumReqiured = general_instructions['General_Instructions'][Dynamic_Adjustment]['Minimum_Required_High']
    MediumLowMinimumReqiured = general_instructions['General_Instructions'][Dynamic_Adjustment]['Minimum_Required_Medium_Low']
    MediumHighMinimumReqiured = general_instructions['General_Instructions'][Dynamic_Adjustment]['Minimum_Required_Medium_High']
    DefaultMinimum = general_instructions['General_Instructions'][Dynamic_Adjustment]['Minimum_Default']

    High_C = price+price*PercentHigh/100>high
    MHigh_C = price+price*PercentMediumHigh/100>high
    Low_C =low+low*PercentLow/100>price
    MLow_C = low+low*PercentMediumLow/100>price

    if Dynamic_Adjustment == 'Dynamic_Adjustment_Short':
        Seed_Strategy = 'Short'
    elif Dynamic_Adjustment == 'Dynamic_Adjustment_Long':
        Seed_Strategy = 'Long'

    if High_C and State != "H": #High
        State = "H"
        general_instructions['General_Instructions'][Dynamic_Adjustment]['State'] = "H"
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Counter_Trigger'] = HighPercentChangeTrigger
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Seed_Size'] = HighSeedSize
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Sell_Threshold_Percentage'] = HighSellThreshHold
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Percent_To_Be_Sold'] = HighPercentToBeSold
        general_instructions['General_Instructions']['USDC']['Minimum_Required'] = HighMinimumReqiured



    elif MHigh_C and State != "MH" and High_C==False: #Medium High
        State = "MH"
        general_instructions['General_Instructions'][Dynamic_Adjustment]['State'] = "MH"
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Counter_Trigger'] = MediumHighPercentChangeTrigger
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Seed_Size'] = MediumHighSeedSize
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Sell_Threshold_Percentage'] = MediumHighSellThreshHold
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Percent_To_Be_Sold'] = MediumHighPercentToBeSold
        general_instructions['General_Instructions']['USDC']['Minimum_Required'] = MediumHighMinimumReqiured

    elif Low_C and State != "L" and MHigh_C == False and High_C == False: #Low
        State = "L"
        general_instructions['General_Instructions'][Dynamic_Adjustment]['State'] = "L"
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Counter_Trigger'] = LowPercentChangeTrigger
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Seed_Size'] = LowSeedSize
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Sell_Threshold_Percentage'] = LowSellThreshHold
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Percent_To_Be_Sold'] = LowPercentToBeSold
        general_instructions['General_Instructions']['USDC']['Minimum_Required'] = LowMinimumReqiured

    elif MLow_C and State != "ML" and MHigh_C == False and High_C == False and Low_C == False: #Medium Low
        State = "ML"
        general_instructions['General_Instructions'][Dynamic_Adjustment]['State'] = "ML"
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Counter_Trigger'] = MediumLowPercentChangeTrigger
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Seed_Size'] = MediumLowSeedSize
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Sell_Threshold_Percentage'] = MediumLowSellThreshHold
        general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Percent_To_Be_Sold'] = MediumLowPercentToBeSold
        general_instructions['General_Instructions']['USDC']['Minimum_Required'] = MediumLowMinimumReqiured
    
    else: #Default
        if State!="D" and MHigh_C == False and High_C == False and Low_C == False and MLow_C == False: 
            State = "D"
            general_instructions['General_Instructions'][Dynamic_Adjustment]['State'] = "D"
            general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Counter_Trigger'] = DefaultTrigger
            general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Seed_Size'] = DefaultSeedSize
            general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Sell_Threshold_Percentage'] = DefaultSellThreshHold
            general_instructions['General_Instructions']['Seeds'][Seed_Strategy]['Percent_To_Be_Sold'] = DefaultPercentToBeSold
            general_instructions['General_Instructions']['USDC']['Minimum_Required'] = DefaultMinimum
    return general_instructions


def LoadInstructions(file_name):
    return json.loads(Path(f"{file_name}.json").read_text())
def WriteInstructions(file_name,altered):
    with open(Path(f"{file_name}.json"), 'w') as json_file:
        json.dump(altered, json_file, indent=4)
def load_log():
    if not LOG_PATH.exists():
        return []       
    text = LOG_PATH.read_text().strip()
    if not text:
        return []            
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        entries = []
        for line in text.splitlines():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries
def write_log_entry(entry: dict):
    with LOG_PATH.open("a") as f:
        f.write(json.dumps(entry))
        f.write("\n")
######## Other ###################################
def Time_Conversion(hours):
    readable_times = [time(h).strftime("%#I:%M%p").lower() for h in hours]
    return readable_times