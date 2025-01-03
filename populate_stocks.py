import sqlite3, config
import alpaca_trade_api as tradeapi

connection = sqlite3.connect(config.DB_FILE)
connection.row_factory = sqlite3.Row


cursor = connection.cursor()

cursor.execute("""
    SELECT symbol, name FROM stock
""")

rows = cursor.fetchall()
symbols = [row['symbol'] for row in rows]
print(symbols)


api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url = config.API_URL)
assets = api.list_assets()

for asset in assets:
    try:
        # Filter only for valid US stocks (equity) listed on NASDAQ or NYSE
        if asset.exchange in ['NASDAQ', 'NYSE'] and asset.status == 'active' and asset.tradable:
            if asset.status == 'active' and asset.tradable and getattr(asset, 'class') == 'us_equity':
                print(f"Added a new stock {asset.symbol} {asset.name}")
                cursor.execute(
                    "INSERT INTO stock(symbol, name, exchange) VALUES (?, ?, ?)",
                    (asset.symbol, asset.name, asset.exchange)
                )
    except Exception as e:
        print(f"Error adding stock {asset.symbol}: {e}")




connection.commit()