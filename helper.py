from pathlib import Path
from datetime import time
import http.client
import json
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
def MyBTCAccount(client,accounts):
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
######### Handles json files #####################
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