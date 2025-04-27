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
    while helper.ManualStop(instructions):
        try:
            BTC = helper.BTCValue(client,accounts)
            USDC = helper.USDCValue(accounts)
            print('BTC+USDC Total: ', BTC+USDC)
            print('BTC: ', BTC)
            print('USDC: ', USDC)
            #print('Testing: ',helper.UpperThreshold(instructions))

            #when the BTC value goes up sell and when it goes down buy
            if helper.BTCValue(client,accounts)>helper.UpperThresholdAmount(instructions):
                helper.SellBTC(client,instructions)
                instructions = helper.DecrementCounter(instructions)

            elif helper.BTCValue(client,accounts)<helper.LowerThresholdAmount(instructions) and GetStopCounterActive(instructions)==False:
                helper.BuyBTC(client,instructions)
                instructions = helper.IncrementCounter(instructions)
                if helper.GetCounter(instructions)==helper.GetStopCounter(instructions):# if counter == stop change stop counter to true.
                    instructions=helper.ChangeCounterActive(instructions)
        

            if USDC>helper.GetUSDCBaseBalance(instructions):
                order = helper.BalanceIncreaseReadjust(client,instructions)
                print(order)
                if order['success']:
                    instructions = helper.IncreaseUSDCBalance(instructions)
                    instructions = helper.IncreaseBTCBalance(instructions)
                else:
                    print('Order Failed', order['error_response'])

            if helper.GetCounter(instructions)==0 and helper.GetStopCounterActive(instructions):#if 0 and active
                instructions=helper.ChangeCounterActive(instructions)#switch stop active counter to false
            #elif helper.GetStopCounterActive(instructions):
            #    instructions = helper.DecrementCounter(instructions)# if getCounter is active then slowly bring the decrement counter down.
        except Exception as e:
            helper.write_log_entry({"time": time.time(),"error": str(e)})
        helper.WriteInstructions(instructions)
        time.sleep(60)
        instructions = helper.LoadInstructions()
        


def main():
    client = RESTClient(api_key=api_key,api_secret=api_secret)
    accounts = client.get_accounts()
    instructions = helper.LoadInstructions()
    print(instructions)
    loop(client,accounts,instructions)


if __name__ == "__main__":
    main()
