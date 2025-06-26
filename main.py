from coinbase.rest import RESTClient
from dotenv import load_dotenv
from datetime import datetime
import os
import helper
import time


load_dotenv()


api_key = os.getenv('Coinbase_API_Key_Name')
api_secret = os.getenv('Coinbase_Private_Key')



def main():
    try:
        client = RESTClient(api_key=api_key,api_secret=api_secret)
        accounts = client.get_accounts()
        general_instructions=helper.LoadInstructions("general_instructions")
        DActive = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['Active']

        if DActive:
            general_instructions=helper.Dynamic_update(client,general_instructions)
        

        Active = general_instructions['General_Instructions']['Manual_Stop']       
        Timer = general_instructions['General_Instructions']['Timer']
        Counter = general_instructions['General_Instructions']['Counter']
        CounterMax = general_instructions['General_Instructions']['Counter_Max']
        ShortCounter = general_instructions['General_Instructions']['Seeds']['Short']['Short_Counter_Trigger']
        ShortSeedSize = general_instructions['General_Instructions']['Seeds']['Short']['Seed_Size']
        ShortSeedSellThresh = general_instructions['General_Instructions']['Seeds']['Short']['Sell_Threshold_Percentage']
        LongCounter = general_instructions['General_Instructions']['Seeds']['Long']['Long_Counter_Trigger']
        LongSeedSize = general_instructions['General_Instructions']['Seeds']['Long']['Seed_Size']
        LongSeedSellThresh = general_instructions['General_Instructions']['Seeds']['Long']['Sell_Threshold_Percentage']
        USDCMin=general_instructions['General_Instructions']['USDC']['Minimum_Required']


        if Active:
            if helper.MyUSDCValue(accounts) >= USDCMin:
                if Counter%ShortCounter==0:
                    buyReply = helper.BuyBTC(client,ShortSeedSize)
                    time.sleep(Timer)
                    orderId = buyReply['success_response']['order_id']
                    orderInfo = helper.OrderInfo(client,orderId)
                    sellReply=helper.SellBTCLimit(client,orderInfo,ShortSeedSellThresh)
                if Counter%LongCounter==0:
                    time.sleep(Timer)
                    buyReply = helper.BuyBTC(client,LongSeedSize)
                    time.sleep(Timer)
                    orderId = buyReply['success_response']['order_id']
                    orderInfo = helper.OrderInfo(client,orderId)
                    sellReply=helper.SellBTCLimit(client,orderInfo,LongSeedSellThresh)
                    print(sellReply)
                if general_instructions['General_Instructions']['Counter']+1<=CounterMax:
                    general_instructions['General_Instructions']['Counter']+=1
                else:
                     general_instructions['General_Instructions']['Counter']=1
                helper.WriteInstructions("general_instructions",general_instructions)
    except Exception as e:
            helper.write_log_entry({"time": str(datetime.now()),"error": str(e)})

if __name__ == "__main__":
    main()
