import sqlite3
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 1. Connect to a local database file (Python will create 'shoes.db' automatically!)
conn = sqlite3.connect("shoes.db", check_same_thread=False)
cursor = conn.cursor()

# 2. Create our database table if it doesn't exist yet
cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT,
        model TEXT,
        price REAL,
        in_stock BOOLEAN
    )
""")
conn.commit()

# Our Shoe Blueprint
class Shoe(BaseModel):
    brand: str
    model: str
    price: float
    in_stock: bool

@app.get("/")
def home():
    return {"message": "Welcome to the Persistent Nike API!"}

# 3. GET Route: Read from the Database
@app.get("/inventory")
def get_inventory():
    # Ask the database for all the shoes
    cursor.execute("SELECT brand, model, price, in_stock FROM inventory")
    rows = cursor.fetchall()
    
    # Format the raw database rows into a nice, readable list
    inventory_list = []
    for row in rows:
        inventory_list.append({
            "brand": row[0], 
            "model": row[1], 
            "price": row[2], 
            "in_stock": bool(row[3])
        })
    return inventory_list

# 4. POST Route: Write to the Database
@app.post("/inventory")
def add_shoes(new_shoes: List[Shoe]):
    # Loop through the list of shoes and insert them into the database one by one
    for shoe in new_shoes:
        cursor.execute(
            "INSERT INTO inventory (brand, model, price, in_stock) VALUES (?, ?, ?, ?)",
            (shoe.brand, shoe.model, shoe.price, shoe.in_stock)
        )
    # Save the changes
    conn.commit()
    return {"message": f"Success! Saved {len(new_shoes)} shoes to the database permanently."}