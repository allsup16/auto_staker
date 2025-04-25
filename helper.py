from pathlib import Path
import json
import numpy as np

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

def LoadInstructions():
    file_path = Path('instruction.json')
    data = json.loads(file_path.read_text())
    return data

def WriteInstructions(altered):
    file_name = 'instruction.json'
    with open(file_name, 'w') as json_file:
        json.dump(altered, json_file, indent=4)


def LowerThreshold(instructions):
    lowerThreshold = (instructions['Lower-Threshold']/100)*instructions['Base_Balance']
    return lowerThreshold

def UpperThreshold(instructions):
    lowerThreshold = (instructions['Upper-Threshold']/100)*instructions['Base_Balance']
    return lowerThreshold

