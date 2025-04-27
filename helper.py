from pathlib import Path
import json
import numpy as np
import uuid


LOG_PATH = Path("log.json")
INSTUCTIONS_PATH =Path('instruction.json')


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
def BTCValue(client,accounts):
    amount=0
    for x in accounts.accounts:
        if x.name == 'BTC Wallet':
            product = client.get_product(f"{x.currency}-USD")
            amount=np.round(np.float64(product.price),decimals=0)*np.float64(x.available_balance['value'])
    return amount    
def USDCValue(accounts):
    amount=0
    for x in accounts.accounts:
        if x.name == 'USDC Wallet':
            amount= np.float64(x.available_balance['value'])
    return amount    
def BuyBTC(client,instructions):
    size = LowerThreshold(instructions)
    order = client.market_order_buy(client_order_id=str(uuid.uuid4()), product_id="BTC-USDC", quote_size=f"{size:.8f}")
    return order
def SellBTC(client,instructions):
    size = UpperThreshold(instructions)
    order = client.market_order_sell(client_order_id=str(uuid.uuid4()), product_id="BTC-USDC", quote_size=f"{size:.8f}")
    return order
def BalanceIncreaseReadjust(client,instructions):
    size = instructions['Increase_Base_Amounts_flat']
    order = client.market_order_buy(client_order_id=str(uuid.uuid4()), product_id="BTC-USDC", quote_size=f"{size:.8f}")
    return order
########## Interacts with instructions section #########
def ManualStop(instructions)->bool:
    return instructions['Manual_Stop']
def GetUSDCBaseBalance(instructions):
    return instructions['Base_USDC_Balance']
def GetStopCounterActive(instructions):
    return instructions['Stop_Trade_Active']
def GetCounter(instructions):
    return instructions['Counter']
def GetStopCounter(instructions):
    return instructions['Stop_Counter']
def GetCounterMultiplier(instructions):
    return instructions['Counter_Multiplier']
#difference between threshhold and balance (sell) (ammount difference)
def UpperThreshold(instructions):
    upperThreshold = ((instructions['Upper-Threshold_Percentage']/100)*instructions['Counter_Multiplier'])*instructions['Base_BTC_Balance']
    return upperThreshold
#difference between threshhold and balance (buy) (amount difference)
def LowerThreshold(instructions):
    lowerThreshold = (instructions['Lower-Threshold_Percentage']/100)*instructions['Base_BTC_Balance']
    return lowerThreshold
#totals between threshhold and balance (sell) (totals)
def UpperThresholdAmount(instructions):
    return instructions['Base_BTC_Balance']+UpperThreshold(instructions)
#total between threshhold and balance (buy) (totals)
def LowerThresholdAmount(instructions):
    return instructions['Base_BTC_Balance']-LowerThreshold(instructions)
#increase the USDC balance (for scaling up) 
def IncreaseUSDCBalance(instructions):
    instructions['Base_USDC_Balance'] = instructions['Base_USDC_Balance']+instructions['Increase_Base_Amounts_flat']
    return instructions
#increase the BTC balance (for scaling up)
def IncreaseBTCBalance(instructions):
    instructions['Base_BTC_Balance'] = instructions['Base_BTC_Balance']+instructions['Increase_Base_Amounts_flat']
    return instructions
#Not used but may use in future strategies
def DecreaseUSDCBalance(instructions):
    print('DecreaseUSDCBalance Code')
#Not used but may use in future strategies
def DecreaseBTCBalance(instructions):
    print('DecreaseUSDCBalance Code')
#When buying increment counter 
def IncrementCounter(instructions):
    instructions['Counter']+=1
    return instructions
#When selling or during pause purchase decrese counter
def DecrementCounter(instructions):
    if instructions['Counter']-1 <0:
        pass
    else:
        instructions['Counter']-=1 
    return instructions
#When buying purchase increse multiplier
def IncrementMultiplier(instructions):
    if instructions['Counter_Multiplier']+1>instructions['Stop_Counter']:
        pass
    else:
        instructions['Counter']+=1 
    return instructions
#When buying purchase decrese multiplier
def DecrementMultiplier(instructions):
    if instructions['Counter']-1 <1:
        pass
    else:
        instructions['Counter']-=1 
    return instructions
#Change if the stop trade activity
def ChangeCounterActive(instructions):
    if instructions['Stop_Trade_Active']:
        instructions['Stop_Trade_Active']=False
    else:
        instructions['Stop_Trade_Active']=True
    return instructions
######### Handles json files #####################
def LoadInstructions():
    return json.loads(INSTUCTIONS_PATH.read_text())
def WriteInstructions(altered):
    with open(INSTUCTIONS_PATH, 'w') as json_file:
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