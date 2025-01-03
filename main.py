import sqlite3, config
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from pathlib import Path
from starlette.requests import Request
from fastapi.responses import JSONResponse
from datetime import date
from fastapi.responses import RedirectResponse, JSONResponse



app = FastAPI()

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

@app.get("/")
def index(request: Request):
    stock_filter = request.query_params.get('filter', False)
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row


    cursor = connection.cursor()

    if stock_filter == "new_closing_highs":
        cursor.execute("""
            SELECT symbol, name, stock_id, close, date
            FROM stock_price
            JOIN stock ON stock.id = stock_price.stock_id
            WHERE close = (
                SELECT MAX(close)
                FROM stock_price sp2
                WHERE sp2.stock_id = stock_price.stock_id
            )
            AND date = ?
            ORDER BY symbol;
        """, (date.today().isoformat(),))
    elif stock_filter == "new_closing_lows":
        cursor.execute("""
            SELECT symbol, name, stock_id, close, date
            FROM stock_price
            JOIN stock ON stock.id = stock_price.stock_id
            WHERE close = (
                SELECT MIN(close)
                FROM stock_price sp2
                WHERE sp2.stock_id = stock_price.stock_id
            )
            AND date = ?
            ORDER BY symbol;
        """, (date.today().isoformat(),))

    else:
        cursor.execute("""
            SELECT id, symbol, name FROM stock ORDER BY symbol
        """)

    rows = cursor.fetchall()
    
    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows})

@app.get("/stock/{symbol}")
def stock_detail(request: Request, symbol):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(""" 
        SELECT * FROM strategy
    """)

    strategies = cursor.fetchall()
    # Fetch stock details and print debug info
    cursor.execute("""
        SELECT id, symbol, name FROM stock WHERE symbol = ?
    """, (symbol,))
    row = cursor.fetchone()
    print(f"Stock query for symbol {symbol}:")
    print(f"Stock row data: {dict(row) if row else 'None'}")

    if row is None:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Stock not found"})

    # Debug: Print the stock ID we're using
    stock_id = row['id']
    print(f"Looking for prices with stock_id: {stock_id}")

    # Debug: First check if any prices exist
    cursor.execute("SELECT COUNT(*) as count FROM stock_price WHERE stock_id = ?", (stock_id,))
    count = cursor.fetchone()['count']
    print(f"Number of price records found: {count}")

    # Fetch prices with original query
    cursor.execute("""
        SELECT date, open, high, low, close, volume 
        FROM stock_price 
        WHERE stock_id = ? 
        ORDER BY date DESC
    """, (stock_id,))
    prices = cursor.fetchall()
    
    # Debug: Print first few prices if any exist
    if prices:
        print("First few prices:")
        for price in prices[:3]:
            print(dict(price))
    else:
        print("No prices found")

    return templates.TemplateResponse("stock_detail.html", {
        "request": request,
        "stock": row,
        "bars": prices,
        "strategies": strategies
    })

@app.post("/apply_strategy")
def apply_strategy(strategy_id: int = Form(...), stock_id: int = Form(...)):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO stock_strategy (stock_id, strategy_id) VALUES (?, ?)
        """, (stock_id, strategy_id))
        connection.commit()
    except sqlite3.IntegrityError as e:
        return JSONResponse(content={"error": "Invalid stock or strategy ID"}, status_code=400)

    return RedirectResponse(url=f"/strategy/{strategy_id}", status_code=303)


@app.get("/strategy/{strategy_id}")
def strategy(request: Request, strategy_id):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name
        FROM strategy
        WHERE id = ?
    """, (strategy_id,))

    strategy = cursor.fetchone()

    cursor.execute("""
        SELECT symbol, name
        FROM stock JOIN stock_strategy on stock_strategy.stock_id = stock.id
        WHERE strategy_id = ?
    """, (strategy_id,))

    stocks = cursor.fetchall()

    return templates.TemplateResponse("strategy.html", {"request":request,
    "stocks": stocks, "strategy":strategy})