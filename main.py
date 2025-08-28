from coinbase.rest import RESTClient
from dotenv import load_dotenv
from datetime import datetime,timezone
import traceback
import sheets
import os
import helper
import time


load_dotenv()


api_key = os.getenv('Coinbase_API_Key_Name')
api_secret = os.getenv('Coinbase_Private_Key')
#with open("/root/auto_staker/logs/cron.log", "a") as log:                                                                   
#    log.write(f"\n[{datetime.now(timezone.utc)}] main.py started\n")


def main():
    try:
        client = RESTClient(api_key=api_key,api_secret=api_secret)
        accounts = client.get_accounts()
        general_instructions=helper.LoadInstructions("general_instructions")
        DActive = general_instructions['General_Instructions']['Dynamic_Adjustment_Short']['Active']
        Sheets = general_instructions['General_Instructions']['Sheets']
        if DActive:
            general_instructions=helper.Dynamic_update(client,general_instructions)
        

        Active = general_instructions['General_Instructions']['Manual_Stop']       
        Timer = general_instructions['General_Instructions']['Timer']
        Counter = general_instructions['General_Instructions']['Counter']
        CounterMax = general_instructions['General_Instructions']['Counter_Max']

        ShortActiveBuy = general_instructions['General_Instructions']['Seeds']['Short']['Active_Buy']
        ShortCounter = general_instructions['General_Instructions']['Seeds']['Short']['Counter_Trigger']
        ShortSeedSize = general_instructions['General_Instructions']['Seeds']['Short']['Seed_Size']
        ShortActiveSell = general_instructions['General_Instructions']['Seeds']['Short']['Active_Sell']
        ShortSeedSellThresh = general_instructions['General_Instructions']['Seeds']['Short']['Sell_Threshold_Percentage']
        ShortPecentToBeSold = general_instructions['General_Instructions']['Seeds']['Short']['Percent_To_Be_Sold']
        ShortUSDCMin=general_instructions['General_Instructions']['Seeds']['Short']['Minimum_Required']

        LongActiveBuy = general_instructions['General_Instructions']['Seeds']['Long']['Active_Buy']
        LongCounter = general_instructions['General_Instructions']['Seeds']['Long']['Counter_Trigger']
        LongSeedSize = general_instructions['General_Instructions']['Seeds']['Long']['Seed_Size']
        LongActiveSell = general_instructions['General_Instructions']['Seeds']['Long']['Active_Sell']
        LongSeedSellThresh = general_instructions['General_Instructions']['Seeds']['Long']['Sell_Threshold_Percentage']
        LongPecentToBeSold = general_instructions['General_Instructions']['Seeds']['Long']['Percent_To_Be_Sold']
        LongUSDCMin=general_instructions['General_Instructions']['Seeds']['Long']['Minimum_Required']

        value =helper.MyUSDCValue(accounts)

        if Active:
            if value >= ShortUSDCMin:
                if Counter%ShortCounter==0:
                    if ShortActiveBuy:
                        buyReply = helper.BuyBTC(client,ShortSeedSize)
                        time.sleep(Timer)
                        orderId = buyReply['success_response']['order_id']
                        orderInfo = helper.OrderInfo(client,orderId)
                        if ShortActiveSell:
                            sellReply=helper.SellBTCLimit(client,orderInfo,ShortSeedSellThresh,ShortPecentToBeSold)
                
            time.sleep(Timer)
            if value >= LongUSDCMin:
                if Counter%LongCounter==0:
                    if LongActiveBuy:
                        buyReply = helper.BuyBTC(client,LongSeedSize)
                        time.sleep(Timer)
                        orderId = buyReply['success_response']['order_id']
                        orderInfo = helper.OrderInfo(client,orderId)
                        if LongActiveSell:
                            sellReply=helper.SellBTCLimit(client,orderInfo,LongSeedSellThresh,LongPecentToBeSold)
                            print(sellReply)

                if general_instructions['General_Instructions']['Counter']+1<=CounterMax+1:
                    general_instructions['General_Instructions']['Counter']+=1
                else:
                     general_instructions['General_Instructions']['Counter']=1
                helper.WriteInstructions("general_instructions",general_instructions)

            #if Sheets["Active"] or Sheets["Test"]:
            #    print('Cred:\n')
            #    cred = sheets.sheets_auth(Sheets)
            #    print("Insert:\n")
            #    sheets.insert_value(Sheets,cred,True)    
    except Exception as e:
            print("".join(traceback.format_exception(type(e), e, e.__traceback__)))

if __name__ == "__main__":
    main()
