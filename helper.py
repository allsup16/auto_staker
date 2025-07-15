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
def SellBTCLimit(client,orderInfo,SeedSellThresh):
    try: 
        clientId = str(uuid.uuid4())
        productId = orderInfo['order']['product_id']
        filledSize = float(orderInfo['order']['filled_size'])
        boughtPrice = float(orderInfo['order']['average_filled_price'])
        targetSalePrice = boughtPrice + boughtPrice * (SeedSellThresh / 100)
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
        low = price
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
    DState = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['State']
    DPercentLow = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['Percent_Low']
    DPercentHigh = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['Percent_High']
    DPercentLowChangeTrigger = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['Percent_Low_Change_Trigger']
    DPercentHighChangeTrigger = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['Percent_High_Change_Trigger']
    DDefaultTrigger = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['Default_Trigger']
    DMinimumReqiuredLow = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['Minimum_Required_Low']
    DMinimumReqiuredHigh = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['Minimum_Required_High']
    DMinimumDefault = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['Default_Minimum']

    if price+price*DPercentHigh/100>high and DState != "H":
        general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['State'] = "H"
        general_instructions['General_Instructions']['Seeds']['Short']['Short_Counter_Trigger'] = DPercentHighChangeTrigger
        general_instructions['General_Instructions']['USDC']['Minimum_Required'] = DMinimumReqiuredHigh
        WriteInstructions("general_instructions",general_instructions)
    elif low+low*DPercentLow/100>price and DState != "L":
        general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['State'] = "L"
        general_instructions['General_Instructions']['Seeds']['Short']['Short_Counter_Trigger'] = DPercentLowChangeTrigger
        general_instructions['General_Instructions']['USDC']['Minimum_Required'] = DMinimumReqiuredLow
        WriteInstructions("general_instructions",general_instructions)
    elif DState != "D" and low+low*DPercentLow/100<price and price+price*DPercentHigh/100<high:
        general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['State'] = "D"
        general_instructions['General_Instructions']['Seeds']['Short']['Short_Counter_Trigger'] = DDefaultTrigger
        general_instructions['General_Instructions']['USDC']['Minimum_Required'] = DMinimumDefault
        WriteInstructions("general_instructions",general_instructions)
    print(price)
    print("High: ",high)
    print('Low: ',low+low*DPercentLow/100)
    print('High: ',price+price*DPercentHigh/100)
    return LoadInstructions("general_instructions")
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