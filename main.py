from coinbase.rest import RESTClient
from dotenv import load_dotenv
import numpy as np
import os
import helper
import time

load_dotenv()


api_key = os.getenv('Coinbase_API_Key_Name')
api_secret = os.getenv('Coinbase_Private_Key')

def loop(client,accounts,instructions):
    active = True
    while active:
        BTC = helper.BTCValue(client,accounts)
        USDC = helper.USDCValue(accounts)
        print('BTC+USDC Total: ', BTC+USDC)
        print('BTC: ', BTC)
        print('USDC: ', USDC)
        time.sleep(60)
        active = False


def main():
    client = RESTClient(api_key=api_key,api_secret=api_secret)
    accounts = client.get_accounts()
    instructions = helper.LoadInstructions()
    print(instructions)
    loop(client,accounts,instructions)


if __name__ == "__main__":
    main()
