# Stock Trading App

A Python-based stock trading application that uses a SQLite database to store user, stock, and transaction data. This repo demonstrates a simple end-to-end prototype for buying and selling stocks, tracking user balances, and displaying a minimal user interface.

---

## Table of Contents
1. [Features](#features)  
2. [Installation](#installation)  
3. [Usage](#usage)  
4. [Project Structure](#project-structure)  
5. [Database Schema](#database-schema)  
6. [Screenshots](#screenshots)  
7. [License](#license)

---

## Features

- **User Registration & Authentication**: Securely create accounts and log in.  
- **Portfolio Management**: Monitor holdings and account balance.  
- **Real-Time Trading (Prototype)**: Buy and sell stocks with data stored in SQLite.  
- **Transaction History**: Keep track of all user transactions in the database.  
- **Web-Based Interface**: Simple HTML-based UI for ease of use.
- **Administative Features**: Admin can create stocks and manage market hours.

---

## Installation

1. **Clone or Download the Repository**  
   ```bash
   git clone https://github.com/danekentjensen/Stock-Trading-App.git
   cd Stock-Trading-App
2. **(Recommended) Create & Activate a Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
3. **Install Dependencies:**
   - Make sure you have Python 3.7+ installed. Then run:
   ```bash
   pip install -r requirements.txt
4. **Check the SQLite Database**
   - By default, the project should contain a pre-populated SQLite file (ndc_trading.db)

---

## Usage

1. **Run the Application**
   ```bash
   python app.py
   # This may start a local development server at http://127.0.0.1:5000 (depending on how your Flask or other framework is configured).
2. **Access in Your Browser**
   - Go to http://127.0.0.1:5000 to view the application.
   - Sign up for an account to login or use existing login (**Username:** johndoe **Password:** password123)
   - Explore the portfolio page to see holdings.
   - Buy or sell stock (If stock market is open. If it is closed you can change market hours on admin login page.
   - Check transaction history.
   - To view Admin login use: **Username:** admin **Password:** P@ssw0rd! 
3. **Stop the Server**
   - Press Ctrl + C in the terminal window to stop the local server.
     
---

## Project Structure

      Stock-Trading-App/
      ├── templates/
      │   ├── index.html
      │   ├── account_home.html
      │   ├── cash_management.html
      │   ├── create_account.html
      │   ├── forget_password.html
      │   ├── portfolio.html
      │   ├── stock_details.html
      │   ├── transaction_history.html
      │   ├── admin.html
      │   └── watchlist.html
      ├── static/
      │   ├── styles.css
      │   └── stockApp.js
      ├── app.py               # Main application (Flask or another framework)
      ├── ndc_trading.db          # SQLite database file 
      ├── requirements.txt     # Python dependencies
      └── README.md            # This file

---

## Database Schema

      CREATE TABLE Users (
          UserID INTEGER PRIMARY KEY AUTOINCREMENT,
          FullName TEXT NOT NULL,
          Email TEXT NOT NULL UNIQUE,
          Username TEXT NOT NULL UNIQUE,
          Password TEXT NOT NULL,
          CashBalance REAL DEFAULT 10000.00 -- Default cash balance
      );
      
      CREATE TABLE Stocks (
          StockID INTEGER PRIMARY KEY AUTOINCREMENT,
          Symbol TEXT NOT NULL UNIQUE,
          CompanyName TEXT NOT NULL,
          CurrentPrice REAL NOT NULL,
      	Volume INTEGER NOT NULL DEFAULT 0, 
      	OpeningPrice REAL NOT NULL DEFAULT 0.0, 
      	DayHigh REAL NOT NULL DEFAULT 0.0, 
      	DayLow REAL NOT NULL DEFAULT 0.0);
      	
      CREATE TABLE Transactions (
          TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
          UserID INTEGER NOT NULL,
          StockID INTEGER NOT NULL,
          Quantity INTEGER NOT NULL,
          PricePerShare REAL NOT NULL,
          TransactionType TEXT NOT NULL CHECK(TransactionType IN ('BUY', 'SELL')),
          TransactionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (UserID) REFERENCES Users(UserID),
          FOREIGN KEY (StockID) REFERENCES Stocks(StockID)
      );
      
      CREATE TABLE Transactions_DW (
          Transaction_ID INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique ID for each transaction
          UserID INTEGER NOT NULL,                            -- User performing the transaction
          Transaction_Type TEXT NOT NULL CHECK(Transaction_Type IN ('DEPOSIT', 'WITHDRAWAL')), -- Transaction type
          Amount REAL NOT NULL CHECK(Amount > 0),             -- Positive transaction amount
          Transaction_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Date and time of the transaction
          FOREIGN KEY (UserID) REFERENCES Users(UserID)       -- Foreign key linking to Users table
      );
      
      CREATE TABLE Portfolios (
          PortfolioID INTEGER PRIMARY KEY AUTOINCREMENT,
          UserID INTEGER NOT NULL,
          StockID INTEGER NOT NULL,
          Quantity INTEGER NOT NULL,
          FOREIGN KEY (UserID) REFERENCES Users(UserID),
          FOREIGN KEY (StockID) REFERENCES Stocks(StockID),
          UNIQUE (UserID, StockID) -- Ensure one entry per user-stock pair
      );
      
      CREATE TABLE IF NOT EXISTS "Market_Hours" (
          Market_Hours_ID INTEGER PRIMARY KEY AUTOINCREMENT,
          Start_Time TEXT,
          End_Time TEXT,
          Day_of_the_Week TEXT NOT NULL,
      	Holiday_Closed INTEGER DEFAULT 0..s
      );
      	
      CREATE TABLE Admins (
          AdminID INTEGER PRIMARY KEY AUTOINCREMENT,
          Username TEXT UNIQUE NOT NULL,
          Password TEXT NOT NULL
      );

---

## Screenshots
1. Login Screen
   ![image](https://github.com/user-attachments/assets/362b7f9f-d90d-410f-85f3-f480e6fa2681)
   
2. Account Creation Screen
   ![image](https://github.com/user-attachments/assets/e12d8ac9-5174-4b38-aa8e-8fb9c1d2a6c5)
   
3. User Account Home
   ![image](https://github.com/user-attachments/assets/65d50e54-027d-44ee-9e74-a586c98ee54c)
   
4. Stock Watchlist Screen
   ![image](https://github.com/user-attachments/assets/6b7bf544-8f67-445e-b737-9b8c0daabb5a)
   
5. Stock Details Screen (User can purchase or sell stocks at current market price)
   ![image](https://github.com/user-attachments/assets/b21dfd6a-73f1-42c1-809c-9686662cef4f)
   
6. User Portfolio Screen
   ![image](https://github.com/user-attachments/assets/8377f416-5c9e-425d-a0d2-548389fb7423)

7. User Transaction History
   ![image](https://github.com/user-attachments/assets/425edfb4-4ae6-4bcc-84f3-9bdd9b68e906)

8.User Cash Management (Ability to depost or withdraw)
   ![image](https://github.com/user-attachments/assets/d3d52225-530c-42e7-af44-c766cda3af96)

9. Admin Dashboard (Ability to create new stocks and manage market hours)
    ![image](https://github.com/user-attachments/assets/1dbeb05f-888f-412e-a57e-f622d229c0dd)

---

## License

This project is licensed under the [MIT License](LICENSE).







   

