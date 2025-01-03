import sqlite3, config

try:
    # Connect to database
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    # Debug: Print connection confirmation
    print("Connected to database:", config.DB_FILE)

    # Create 'stock' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock(
            id INTEGER PRIMARY KEY,
            symbol TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            exchange TEXT NOT NULL
        )
    """)
    print("Created table: stock")

    # Create 'stock_price' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_price(
            id INTEGER PRIMARY KEY,
            stock_id INTEGER,
            date TEXT NOT NULL,
            open REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            close REAL NOT NULL,
            volume INTEGER NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES stock(id)
        )
    """)
    print("Created table: stock_price")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy (
            id INTEGER PRIMARY KEY,
            name NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_strategy(
            stock_id INTEGER NOT NULL,
            strategy_id INTEGER NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES stock (id)
            FOREIGN KEY (strategy_id) REFERENCES strategy (id)
        )
    """)

    strategies = ['opening_range_breakout', 'opening_range_breakdown']

    cursor.execute("SELECT name FROM strategy")
    existing_strategies = {row[0] for row in cursor.fetchall()}  # Use a set for quick lookup

    for strategy in strategies:
        if strategy not in existing_strategies:
            cursor.execute("""
                INSERT INTO strategy (name) VALUES (?)
            """, (strategy,))



    # Commit changes and close connection
    connection.commit()
    connection.close()
    print("Database created successfully.")

except sqlite3.Error as e:
    print("SQLite error:", e)
