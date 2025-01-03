import sqlite3, config

connection = sqlite3.connect(config.DB_FILE)
cursor = connection.cursor()

# Drop tables only if they exist
cursor.execute("DROP TABLE IF EXISTS stock_price;")
cursor.execute("DROP TABLE IF EXISTS stock;")

connection.commit()
connection.close()
