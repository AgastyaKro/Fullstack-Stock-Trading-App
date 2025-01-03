import sqlite3
import config
import alpaca_trade_api as tradeapi
from datetime import date
import pandas as pd
import time
from requests.exceptions import HTTPError

# Database connection
connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row

cursor = connection.cursor()

# Get strategy ID
cursor.execute("""
    select id from strategy where name = 'opening_range_breakout'
""")
strategy_id = cursor.fetchone()['id']

# Fetch stocks linked to strategy
cursor.execute("""
    select symbol, name
    from stock
    join stock_strategy on stock_strategy.stock_id = stock.id
    where stock_strategy.strategy_id = ?
""", (strategy_id,))

stocks = cursor.fetchall()
symbols = [stock['symbol'] for stock in stocks]


current_date = '2021-09-29'
start_minute_bar = f"{current_date} 13:30:00+00:00 "
end_minute_bar = f"{current_date} 13:45:00+00:00 "

# Alpaca API
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

# Fetch historical data
start_date = '2021-09-29'
end_date = '2021-09-30'

orders = api.list_orders(status = 'all', limit = 500, after = f"{current_date}T13:30:00Z")
existing_order_symbols = [order.symbol for order in orders]

# Loop through symbols
for symbol in symbols:
    retry_count = 3
    for attempt in range(retry_count):
        try:
            # Fetch data
            minute_bars = api.get_bars(
                symbol,
                tradeapi.TimeFrame.Minute,
                start=start_date,
                end=end_date
            ).df
            break
        except HTTPError as e:
            print(f"Retrying due to error: {e}")
            time.sleep(2 ** attempt)
    else:
        print(f"Failed to fetch data for {symbol} after {retry_count} attempts.")
        continue

    # Skip if no data
    if minute_bars.empty:
        print(f"No data available for {symbol}. Skipping...")
        continue

    # Filter for opening range
    minute_bars.index = minute_bars.index.tz_convert('UTC')
    opening_range_mask = (minute_bars.index >= pd.Timestamp(start_minute_bar)) & \
                         (minute_bars.index < pd.Timestamp(end_minute_bar))
    opening_range_bars = minute_bars.loc[opening_range_mask]

    if opening_range_bars.empty:
        print(f"No opening range data for {symbol}. Skipping...")
        continue

    # Calculate ranges
    opening_range_low = opening_range_bars['low'].min()
    opening_range_high = opening_range_bars['high'].max()
    opening_range = opening_range_high - opening_range_low

    print(f"{symbol}: Low={opening_range_low}, High={opening_range_high}, Range={opening_range}")

    after_opening_range_mask = minute_bars.index >= end_minute_bar
    after_opening_range_bars = minute_bars.loc[after_opening_range_mask]

    print(after_opening_range_bars)

    after_opening_range_breakout = after_opening_range_bars[after_opening_range_bars['close'] > opening_range_high]

    if not after_opening_range_breakout.empty:
        if symbol not in existing_order_symbols:
            print(after_opening_range_breakout)
            limit_price = after_opening_range_breakout.iloc[0]['close']
            print(limit_price)

            print(f"placing order for {symbol} at {limit_price}, closed_above {opening_range_high} at {after_opening_range_breakout}")

            api.submit_order(
                symbol=symbol,
                side='buy',
                type='limit',
                qty='100',
                time_in_force='day',
                order_class='bracket',
                limit_price=round(limit_price, 2),
                take_profit=dict(
                    limit_price=round(limit_price + opening_range, 2),  # Round to 2 decimals
                ),
                stop_loss=dict(
                    stop_price=round(limit_price - opening_range, 2)   # Round to 2 decimals
                )
            )

        else:
            print(f"Already an order for {symbol}, skipping")


