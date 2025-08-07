Coinbase Automated Trader
Originally created as an auto staker for Etherium, this project became an automated crypto trading system built using the Coinbase SDK and integrated directly with the Coinbase API. The bot uses a scalping-based trading strategy, dynamically adjusting its parameters based on real-time market conditions to optimize trade performance.

Key features:
-Dynamic strategy tuning to adapt to changing volatility and price ranges
-Automated trade execution via the Coinbase API
-Built with Python, leveraging modular design for easy adjustments and monitoring

JSON Instructions Overview
General Controls
Manual_Stop: Halts the script completely when set to true.

Timer: Delay (in seconds) between each execution cycle.

Counter / Counter_Max: Tracks how many times the script has run; resets after reaching the max (e.g., 336 = number of half-hours in a week).

Trade Strategies (Seeds)
Short: Quick-turnover trades aiming for small, frequent profits.

Active_Buy / Active_Sell: Toggle buying or selling on/off.

Short_Counter_Trigger: Counter value (modulo) that triggers a buy.

Seed_Size: Amount of USDC allocated per trade.

Sell_Threshold_Percentage: Target percentage gain for selling.

Percent_To_Be_Sold: Portion of purchased BTC sold at target price.

Long: Long-term trades designed for gradual BTC accumulation.

Long_Counter_Trigger: Counter value that triggers a long-term buy.

Seed_Size: Amount of USDC per long-term trade.

Sell_Threshold_Percentage: Profit target for selling.

Percent_To_Be_Sold: Percentage of BTC sold; remaining BTC is kept for long-term holding.

Capital Management
USDC.Minimum_Required: Minimum USDC balance needed before executing trades.

Market Data
Candles:

Granularity: Timeframe of candlestick data (e.g., ONE_DAY).

Days_Back: Number of days used to determine 30-day highs and lows.

Dynamic_Adjustment_Short: Adjusts short-seed thresholds dynamically.

State: Current state (L = low, H = high, etc.).

Percent_Low / Percent_High: Thresholds for triggering state changes.

Change_Triggers: How many confirmations are required before acting.

Minimum_Required_Low / High: Minimum USDC per state.

Google Sheets Integration
Sheets.Active: Enables logging to Google Sheets.

Scope: API scope for Sheets access.

Service_Account_File: JSON key for Google API authentication.

Spreadsheet_id / Default_Range: Where trade logs are stored.