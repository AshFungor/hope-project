import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
                CREATE TABLE IF NOT EXIST Users
                    (
                    id INTEGER PRIMARY KEY, 
                    name TEXT, 
                    last_name TEXT, 
                    patronymic TEXT, 
                    city_id TEXT FOREIGN KEY,
                    login TEXT, 
                    password TEXT, 
                    sex TEXT, 
                    birthday DATE, 
                    bank_account_id INTEGER
                    ),
                    
                CREATE TABLE IF NOT EXIST Goals
                    (
                    id INTEGER PRIMARY KEY,
                    rate INTEGER,
                    date DATE,
                    bank_account_id INTEGER FOREIGN KEY,
                    complete BOOL DEFAULT FALSE
                    ),
                    
                CREATE TABLE IF NOT EXIST BankAccounts
                    (
                    id INTEGER UNIQUE PRIMARY KEY, 
                    balance INTEGER
                    ),
                    
                CREATE TABLE IF NOT EXIST Companies
                    (
                    id INTEGER PRIMARY KEY,
                    bank_account_id INTEGER FOREIGN KEY
                    ),
                
                CREATE TABLE IF NOT EXIST Deal
                    (
                    id INTEGER PRIMARY KEY,
                    product_id INTEGER FOREIGN KEY,
                    customer_bank_account INTEGER FOREIGN KEY,
                    seller_bank_account INTEGER FOREIGN KEY,
                    count INTEGER,
                    amount INTEGER,
                    status INTEGER,
                    ),
                    
                CREATE TABLE IF NOT EXIST Products2BankAccounts
                    (
                    id INTEGER PRIMARY KEY,
                    bank_account_id INTEGER FOREIGN KEY
                    product_id INTEGER FOREIGN KEY
                    count INTEGER
                    ),
                
                CREATE TABLE IF NOT EXIST Products
                    (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                    )
                
                    
                """)

conn.commit()