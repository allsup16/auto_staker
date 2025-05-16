This project is to create a auto stake trading bot that takes usdc, buy ehtereum and stake's the bought ethereum
I am doing this in order to set the ground work for future crypto trader and learn typescript, get better with git and
learn how to use a hetzner server with linux.


Refactor List:
    split helper method into individual files that target specific functionality.
    implement into hetzner or at least a non local machine.
    switch the writeinstructions to be outside main loop and inside functions that would change the instructions
        -This would limit the amount of rewrites to only happen when needed

json explanation
    "info":
    {
    "Manual_Stop":"Manual way to run the script.",
    "account_set_balance":"Set amount for the account to be balanced around, percentages revolve around this number.",
    "held_amount":"How much is owned within the account",
    "update_increase_amount":"when an update happens, this is the amount the set balance will update by.",
    "access_to_account":"If the account is allowed to make a trade",
    "limit_percentage":"amount allowed to be traded from set balance before trades stop working",
    "limit":"if balance gets below this cost access_to_account becomes false",
    "sell_threshold_percentage":"percentage point that when reached will trigger sell",
    "sell_ammount_Percentage":"percentage point of how much is to be sold",
    "sell_amount":"amount to be sold when trigger is reached",
    "buy_threshold_percentage":"percentage point that when reached will trigger buy",
    "buy_Ammount_Percentage":"percentage point of how much is to be bought",
    "buy_amount":"amount to be bought when trigger is reached",
    "trigger_update_amount":"When this amount is reached update accounts with new balances"
    }