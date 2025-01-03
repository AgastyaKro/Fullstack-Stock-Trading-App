import sqlite3, config
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import time
import logging

# --- Setup Logging ---
logging.basicConfig(filename='errors.log', level=logging.ERROR)

# --- Connect to Database ---
connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()

# --- Fetch Stock Symbols ---
cursor.execute("SELECT id, symbol, name FROM stock")
rows = cursor.fetchall()

# --- Filter Valid Symbols ---
symbols = []
stock_dict = {}
for row in rows:
    symbol = row['symbol']
    # Exclude invalid symbols
    if '/' not in symbol and '.' not in symbol and len(symbol) <= 5 and symbol.isalpha():
        symbols.append(symbol)
        stock_dict[symbol] = row['id']

# --- Connect to Alpaca API ---
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

# --- Date Range ---
start_date = '2023-11-01'
end_date = '2023-12-01'

# --- Chunk Size and Retry Settings ---
chunk_size = 20  # Smaller chunk size to reduce rate-limiting
MAX_RETRIES = 3  # Retry limit
RETRY_DELAY = 3  # Delay between retries in seconds

# --- Early Exit Settings ---
MAX_CHUNKS = 20  # Process only 20 chunks, then exit (REMOVE THIS TO PROCESS ALL SYMBOLS)
processed_chunks = 0  # Counter for processed chunks

# --- Process Symbols in Chunks ---
for i in range(0, len(symbols), chunk_size):
    # --- Check Early Exit ---
    # if processed_chunks >= MAX_CHUNKS:
    #     print("Reached the limit of processed chunks. Exiting script early.")
    #     break

    symbol_chunk = symbols[i:i + chunk_size]
    print(f"Fetching data for symbols: {symbol_chunk}")

    # --- Retry Mechanism ---
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            # Fetch data from API
            barsets = api.get_bars(symbol_chunk, TimeFrame.Day, start=start_date, end=end_date)
            print(f"Total bars fetched: {len(barsets)}")

            # --- Process Each Bar ---
            for bar in barsets:
                symbol = bar.S  # Get symbol from bar
                if symbol not in stock_dict:  # Skip unsupported symbols
                    continue

                stock_id = stock_dict[symbol]

                print(f"Inserting data: {bar}")
                cursor.execute("""
                    INSERT INTO stock_price (stock_id, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (stock_id, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v))
            # --- Commit Changes After Inserting Data ---
            connection.commit()

            # --- Exit Retry Loop if Successful ---
            break
        except Exception as e:
            retry_count += 1
            print(f"Error fetching data for {symbol_chunk}. Retrying {MAX_RETRIES - retry_count} more time(s)...")
            logging.error(f"Error fetching data for {symbol_chunk}: {e}")
            time.sleep(RETRY_DELAY)

    # --- Skip Current Chunk After Max Retries ---
    if retry_count == MAX_RETRIES:
        print(f"Skipping symbols: {symbol_chunk} after {MAX_RETRIES} retries.")
        continue

    # --- Increment Processed Chunks ---
    processed_chunks += 1

    # --- Sleep Between Chunks to Avoid Rate Limits ---
    time.sleep(3)

# --- Commit and Close Database ---
connection.commit()
connection.close()

print("Script completed.")

