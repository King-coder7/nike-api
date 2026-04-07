import sqlite3
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# --- 1. CORS SECURITY ---
# This tells your browser it's safe to let your HTML frontend read this data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. DATABASE SETUP ---
# Connect to the local SQLite file and create the table if it's missing
conn = sqlite3.connect("shoes.db", check_same_thread=False)
cursor = conn.cursor()

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

# --- 3. DATA BLUEPRINT ---
class Shoe(BaseModel):
    brand: str
    model: str
    price: float
    in_stock: bool

# --- 4. API ROUTES ---

@app.get("/")
def home():
    return {"message": "Welcome to the Persistent Nike API!"}

@app.get("/inventory")
def get_inventory():
    # Read all shoes from the database
    cursor.execute("SELECT brand, model, price, in_stock FROM inventory")
    rows = cursor.fetchall()
    
    # Format them into a clean list
    inventory_list = []
    for row in rows:
        inventory_list.append({
            "brand": row[0], 
            "model": row[1], 
            "price": row[2], 
            "in_stock": bool(row[3])
        })
    return inventory_list

@app.post("/inventory")
def add_shoes(new_shoes: List[Shoe]):
    # Save new shoes to the database permanently
    for shoe in new_shoes:
        cursor.execute(
            "INSERT INTO inventory (brand, model, price, in_stock) VALUES (?, ?, ?, ?)",
            (shoe.brand, shoe.model, shoe.price, shoe.in_stock)
        )
    conn.commit()
    return {"message": f"Success! Saved {len(new_shoes)} shoes to the database permanently."}