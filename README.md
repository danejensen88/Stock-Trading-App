# Stock Trading App

A Python-based stock trading application that uses a SQLite database to store user, stock, and transaction data. This repo demonstrates a simple end-to-end prototype for buying and selling stocks, tracking user balances, and displaying a minimal user interface.

---

## Table of Contents
1. [Features](#features)  
2. [Installation](#installation)  
3. [Usage](#usage)  
4. [Project Structure](#project-structure)  
5. [Database Schema](#database-schema)  
6. [Screenshots (Optional)](#screenshots-optional)  
7. [Contributing](#contributing)  
8. [License](#license)

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
   git clone https://github.com/danejensen88/Stock-Trading-App.git
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




   

