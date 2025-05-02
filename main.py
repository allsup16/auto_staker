from coinbase.rest import RESTClient
from dotenv import load_dotenv
from datetime import datetime
import numpy as np
import os
import helper
import time

load_dotenv()


api_key = os.getenv('Coinbase_API_Key_Name')
api_secret = os.getenv('Coinbase_Private_Key')

def loop(client,accounts,instructions):

    while helper.ManualStop(instructions):
        try:
            instructions = helper.LoadInstructions()
            MyBTC = helper.MyBTCValue(client,accounts)
            MyUSDC = helper.MyUSDCValue(accounts)
            print('BTC+USDC Total: ', MyBTC+MyUSDC)
            print('BTC: ', MyBTC)
            print('USDC: ', MyUSDC)

            #buy
            if MyBTC > helper.UpperThresholdAmount(instructions):
                order = helper.SellBTC(client,accounts,instructions)
                if order['success']:
                    instructions = helper.DecrementCounter(instructions)
                else:
                    print('Order Failed', order['error_response'])
            #sell
            elif MyBTC < helper.LowerThresholdAmount(instructions) and helper.GetStopCounterActive(instructions)==False:
                order = helper.BuyBTC(client,instructions)
                if order['success']:
                    instructions = helper.IncrementCounter(instructions)
                    if helper.GetCounter(instructions)==helper.GetStopCounter(instructions):# if counter == stop change stop counter to true.
                        instructions=helper.ChangeCounterActive(instructions)
                else:
                    print('Order Failed', order['error_response'])
        
            #Balance increase
            if MyUSDC > helper.GetUSDCBaseBalance(instructions):
                order = helper.BalanceIncreaseReadjust(client,instructions)
                print(order)
                if order['success']:
                    instructions = helper.IncreaseUSDCBalance(instructions)
                    instructions = helper.IncreaseBTCBalance(instructions)
                else:
                    print('Order Failed', order['error_response'])
            
            #Allowed to but
            if helper.GetCounter(instructions)==0 and helper.GetStopCounterActive(instructions):#if 0 and active
                instructions=helper.ChangeCounterActive(instructions)#switch stop active counter to false

            #update instructions
            helper.WriteInstructions(instructions)
        except Exception as e:
            helper.write_log_entry({"time": str(datetime.now()),"error": str(e)})
        
        time.sleep(60)
        
    
    if helper.ManualStop(instructions)== False:
        BTC = helper.MyBTCValue(client,accounts)
        USDC = helper.MyUSDCValue(accounts)
        print('BTC+USDC Total: ', BTC+USDC)
        print('BTC: ', BTC)
        print('USDC: ', USDC)


def main():
    client = RESTClient(api_key=api_key,api_secret=api_secret)
    accounts = client.get_accounts()
    instructions = helper.LoadInstructions()
    print(instructions)
    loop(client,accounts,instructions)


if __name__ == "__main__":
    main()
