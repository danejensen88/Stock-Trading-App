from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from datetime import datetime
import pytz
import sqlite3
import bcrypt  # For secure password hashing

app = Flask(__name__)

# Secret key
app.secret_key = '45DjnuLj7g58F5Rjud'

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('ndc_trading.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home (Login Page)
@app.route('/')
def index():
    return render_template('index.html')

# Handle Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check credentials in Users table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
    user = cursor.fetchone()

    # If not found in Users, check Admins
    if not user:
        cursor.execute("SELECT * FROM Admins WHERE Username = ?", (username,))
        admin = cursor.fetchone()
        conn.close()

        if admin and bcrypt.checkpw(password.encode('utf-8'), admin['Password'].encode('utf-8')):
            # Redirect admin to the admin dashboard
            session['admin_username'] = admin['Username']
            return redirect(url_for('admin_dashboard'))
        else:
            return "Login failed. Invalid username or password.", 401
    else:
        conn.close()
        if bcrypt.checkpw(password.encode('utf-8'), user['Password'].encode('utf-8')):
            # Redirect regular user to account home
            session['username'] = user['Username']
            session['balance'] = user['CashBalance']
            return redirect(url_for('account_home'))
        else:
            return "Login failed. Invalid username or password.", 401
        
#Forgot Password Page       
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if the email exists in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            # Generate a password reset token (optional)
            reset_token = "example_reset_token"  # Replace with real token generation logic
            # Send an email with the reset link (mocked here)
            print(f"Password reset link: /reset_password?token={reset_token}")
            return "A password reset link has been sent to your email."
        else:
            return "Email not found.", 404

    return render_template('forgot_password.html')

# Handle Logout
@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('index'))  # Redirect to login page

# Account Home Page
@app.route('/account_home')
def account_home():
    # Ensure user is logged in
    if 'username' in session:
        username = session['username']

        # Fetch the updated balance from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT CashBalance FROM Users WHERE Username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            balance = user['CashBalance']
            session['balance'] = balance  # Update the session with the latest balance
            return render_template('account_home.html', username=username, balance=balance)
        else:
            return "User not found.", 404
    else:
        return redirect(url_for('index'))  # Redirect to login page if not logged in


# Create Account Page - GET and POST
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Get form data
        fullname = request.form['fullname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Hash the password for secure storage
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Users (FullName, Email, Username, Password, CashBalance)
                VALUES (?, ?, ?, ?, ?)
            """, (fullname, email, username, hashed_password.decode('utf-8'), 10000.00))  # Default balance of $10,000
            conn.commit()
            conn.close()

            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('Error: Username or email already exists.', 'error')
            return redirect(url_for('create_account'))

    return render_template('create_account.html')

# Watchlist Page
@app.route('/watchlist') 
def watchlist():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Include OpeningPrice in the SELECT query
    cursor.execute("""
        SELECT Symbol, CompanyName, CurrentPrice, Volume, OpeningPrice,
               (Volume * CurrentPrice) AS Capitalization
        FROM Stocks
    """)
    stocks = cursor.fetchall()
    conn.close()
    return render_template('watchlist.html', stocks=stocks)





# Portfolio Page
@app.route('/portfolio')
def portfolio():
    # Ensure user is logged in
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']

    # Fetch the user's portfolio from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Stocks.Symbol, Portfolios.Quantity
        FROM Portfolios
        JOIN Stocks ON Portfolios.StockID = Stocks.StockID
        WHERE Portfolios.UserID = (
            SELECT UserID FROM Users WHERE Username = ?
        )
    """, (username,))
    portfolio = cursor.fetchall()
    conn.close()

    return render_template('portfolio.html', portfolio=portfolio)

# Stock Details Page
@app.route('/stock_details')
def stock_details():
    symbol = request.args.get('symbol')
    if not symbol:
        return "Error: No stock symbol provided.", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch stock details
    cursor.execute("""
        SELECT Symbol, CurrentPrice, OpeningPrice, DayHigh, DayLow, Volume
        FROM Stocks
        WHERE Symbol = ?
    """, (symbol,))
    stock = cursor.fetchone()

    # Get market status
    market_status = is_market_open()  # This should now return a dictionary

    conn.close()

    if stock:
        return render_template('stock_details.html', stock=stock, market_status=market_status)
    else:
        return f"No details available for stock: {symbol}", 404



    
#Transaction History Page
@app.route('/transaction_history')
def transaction_history():
    # Ensure user is logged in
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']

    # Fetch the user's transaction history from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Transactions.TransactionType, Transactions.Quantity, Transactions.PricePerShare, 
               Transactions.TransactionDate, Stocks.Symbol
        FROM Transactions
        JOIN Stocks ON Transactions.StockID = Stocks.StockID
        WHERE Transactions.UserID = (
            SELECT UserID FROM Users WHERE Username = ?
        )
        ORDER BY Transactions.TransactionDate DESC
    """, (username,))
    transactions = cursor.fetchall()
    conn.close()

    return render_template('transaction_history.html', transactions=transactions)
    
#Buy/Sell Logic on Stock Details Page
@app.route('/process_transaction', methods=['POST'])
def process_transaction():
    symbol = request.form['symbol']
    action = request.form['action'].upper()  # Convert to uppercase: "BUY" or "SELL"
    shares = int(request.form['shares'])
    dynamic_price = float(request.form['dynamic_price'])  # Get dynamic price from the frontend

    # Fetch the stock ID from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT StockID FROM Stocks WHERE Symbol = ?", (symbol,))
    stock = cursor.fetchone()

    if not stock:
        conn.close()
        return f"No stock found with symbol: {symbol}", 404

    stock_id = stock['StockID']
    total_cost = dynamic_price * shares

    # Ensure user is logged in
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']

    # Fetch the user's ID and cash balance
    cursor.execute("SELECT UserID, CashBalance FROM Users WHERE Username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return "User not found.", 404

    user_id = user['UserID']
    cash_balance = user['CashBalance']

    # Check if the market is open
    tz = pytz.timezone('America/New_York') 
    now = datetime.now(tz)
    current_time = now.time()
    current_day = now.strftime('%A')  # e.g., "Monday"

    cursor.execute("""
        SELECT Start_Time, End_Time, Holiday_Closed 
        FROM Market_Hours 
        WHERE Day_of_the_Week = ?
    """, (current_day,))
    market_hours = cursor.fetchone()

    if not market_hours:
        conn.close()
        return "Market hours not configured for today.", 500

    start_time = datetime.strptime(market_hours['Start_Time'], '%H:%M').time()
    end_time = datetime.strptime(market_hours['End_Time'], '%H:%M').time()
    holiday_closed = market_hours['Holiday_Closed']

    if holiday_closed or not (start_time <= current_time <= end_time):
        conn.close()
        return "Trades cannot be processed because the market is closed.", 403

    try:
        if action == 'BUY':
            # Check if the user has enough balance
            if cash_balance < total_cost:
                conn.close()
                return "Insufficient funds.", 400

            # Deduct from user's balance
            cursor.execute("""
                UPDATE Users SET CashBalance = CashBalance - ?
                WHERE UserID = ?
            """, (total_cost, user_id))

            # Add to portfolio (update or insert)
            cursor.execute("""
                SELECT Quantity FROM Portfolios WHERE UserID = ? AND StockID = ?
            """, (user_id, stock_id))
            portfolio_entry = cursor.fetchone()

            if portfolio_entry:
                # Update existing portfolio entry
                cursor.execute("""
                    UPDATE Portfolios SET Quantity = Quantity + ?
                    WHERE UserID = ? AND StockID = ?
                """, (shares, user_id, stock_id))
            else:
                # Insert new portfolio entry
                cursor.execute("""
                    INSERT INTO Portfolios (UserID, StockID, Quantity)
                    VALUES (?, ?, ?)
                """, (user_id, stock_id, shares))

            # Record the transaction
            cursor.execute("""
                INSERT INTO Transactions (UserID, StockID, TransactionType, Quantity, PricePerShare)
                VALUES (?, ?, 'BUY', ?, ?)
            """, (user_id, stock_id, shares, dynamic_price))

        elif action == 'SELL':
            # Check if the user owns enough shares
            cursor.execute("""
                SELECT Quantity FROM Portfolios WHERE UserID = ? AND StockID = ?
            """, (user_id, stock_id))
            portfolio_entry = cursor.fetchone()

            if not portfolio_entry or portfolio_entry['Quantity'] < shares:
                conn.close()
                return "Insufficient shares to sell.", 400

            # Add to user's balance
            total_revenue = dynamic_price * shares
            cursor.execute("""
                UPDATE Users SET CashBalance = CashBalance + ?
                WHERE UserID = ?
            """, (total_revenue, user_id))

            # Update the portfolio
            cursor.execute("""
                UPDATE Portfolios SET Quantity = Quantity - ?
                WHERE UserID = ? AND StockID = ?
            """, (shares, user_id, stock_id))

            # Remove stock from portfolio if quantity reaches zero
            cursor.execute("""
                DELETE FROM Portfolios WHERE UserID = ? AND StockID = ? AND Quantity = 0
            """, (user_id, stock_id))

            # Record the transaction
            cursor.execute("""
                INSERT INTO Transactions (UserID, StockID, TransactionType, Quantity, PricePerShare)
                VALUES (?, ?, 'SELL', ?, ?)
            """, (user_id, stock_id, shares, dynamic_price))

        # Commit all changes
        conn.commit()

    except Exception as e:
        conn.rollback()
        conn.close()
        return f"An error occurred: {e}", 500

    conn.close()
    return redirect(url_for('portfolio'))

#Cash Management Page
@app.route('/cash_management')
def cash_management():
    # Ensure the user is logged in
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']

    # Fetch the user's cash balance from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT CashBalance FROM Users WHERE Username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        balance = user['CashBalance']
        return render_template('cash_management.html', balance=balance)
    else:
        return "User not found.", 404

#Cash Management-Deposit Logic
@app.route('/cash_management/deposit', methods=['POST'])
def deposit():
    if 'username' not in session:
        return "Unauthorized", 401

    username = session['username']
    data = request.get_json()
    amount = data.get('amount', 0)

    if amount <= 0:
        return "Invalid deposit amount.", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the user's balance
    cursor.execute("""
        UPDATE Users SET CashBalance = CashBalance + ?
        WHERE Username = ?
    """, (amount, username))
    conn.commit()

    # Fetch the updated balance
    cursor.execute("SELECT CashBalance FROM Users WHERE Username = ?", (username,))
    new_balance = cursor.fetchone()['CashBalance']
    conn.close()

    # Return the new balance
    return {"new_balance": new_balance}, 200

#Cash Management-Withdrawal Logic
@app.route('/cash_management/withdraw', methods=['POST'])
def withdraw():
    if 'username' not in session:
        return "Unauthorized", 401

    username = session['username']
    data = request.get_json()
    amount = data.get('amount', 0)

    if amount <= 0:
        return "Invalid withdrawal amount.", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the current balance
    cursor.execute("SELECT CashBalance FROM Users WHERE Username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return "User not found.", 404

    current_balance = user['CashBalance']
    if amount > current_balance:
        conn.close()
        return "Insufficient funds.", 400

    # Update the user's balance
    cursor.execute("""
        UPDATE Users SET CashBalance = CashBalance - ?
        WHERE Username = ?
    """, (amount, username))
    conn.commit()

    # Fetch the updated balance
    cursor.execute("SELECT CashBalance FROM Users WHERE Username = ?", (username,))
    new_balance = cursor.fetchone()['CashBalance']
    conn.close()

    # Return the new balance
    return {"new_balance": new_balance}, 200


# Test Route
@app.route('/test-db')
def test_db():
    return "Database Test Route!"

# Test Users
@app.route('/test-users')
def test_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT FullName FROM Users;")  # Query to fetch all usernames
    users = cursor.fetchall()
    conn.close()

    if users:
        # Format usernames as a list for display
        fullNames = [user['FullName'] for user in users]
        return f"FullName: {', '.join(fullNames)}"
    else:
        return "No users found in the database."
    

#Update Stock Prices for Stock Generator
@app.route('/update_stock_price', methods=['POST'])
def update_stock_price():
    try:
        # Parse JSON data from the request
        data = request.get_json()
        symbol = data.get('symbol')
        current_price = data.get('currentPrice')
        day_high = data.get('dayHigh')
        day_low = data.get('dayLow')

        # Validate the required fields
        if not all([symbol, current_price, day_high, day_low]):
            return jsonify({'error': 'Invalid data'}), 400

        # Connect to the database and update the stock prices
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Stocks
            SET CurrentPrice = ?, DayHigh = ?, DayLow = ?
            WHERE Symbol = ?
        """, (current_price, day_high, day_low, symbol))
        conn.commit()

        # Return success response
        return jsonify({'success': True, 'message': 'Stock prices updated successfully'}), 200
    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({'error': str(e)}), 500
    finally:
        # Ensure the database connection is always closed
        if 'conn' in locals():
            conn.close()




# Admin Dashboard Page
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_username' not in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch market hours
    cursor.execute("SELECT * FROM Market_Hours")
    market_hours = cursor.fetchall()

    conn.close()

    return render_template('admin.html', username=session['admin_username'], market_hours=market_hours)

# Create New Stock 
@app.route('/create_stock', methods=['POST'])
def create_stock():
    if 'admin_username' not in session:
        return redirect(url_for('index'))

    # Get form data
    company_name = request.form['company_name']
    symbol = request.form['symbol']
    volume = request.form['volume']
    initial_price = request.form['initial_price']

    try:
        # Open database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert stock with initial values, including DayLow and DayHigh
        cursor.execute("""
            INSERT INTO Stocks (CompanyName, Symbol, Volume, CurrentPrice, OpeningPrice, DayLow, DayHigh)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company_name, symbol, volume, initial_price, initial_price, initial_price, initial_price))

        # Commit the transaction
        conn.commit()

        flash('Stock created successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {e}", 'danger')
    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))


#Update Market Hours
@app.route('/update_market_hour', methods=['POST'])
def update_market_hour():
    if 'admin_username' not in session:
        return redirect(url_for('index'))

    market_hour_id = request.form['market_hour_id']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    holiday_closed = 1 if 'holiday_closed' in request.form else 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Market_Hours
        SET Start_Time = ?, End_Time = ?, Holiday_Closed = ?
        WHERE Market_Hours_ID = ?
    """, (start_time, end_time, holiday_closed, market_hour_id))
    conn.commit()
    conn.close()

    flash('Market hours updated successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

def is_market_open():
    from datetime import datetime
    import pytz

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get current day
    today = datetime.now().strftime("%A")
    print(f"Today's day: {today}")

    # Fetch market hours for the current day
    cursor.execute("""
        SELECT Start_Time, End_Time, Day_of_the_Week
        FROM Market_Hours
        WHERE Day_of_the_Week = ?
    """, (today,))
    market_hours = cursor.fetchone()
    conn.close()

    if not market_hours:
        print("No market hours found for today.")
        return {"is_open": False}

    # Unpack market hours
    start_time_str, end_time_str, day_of_the_week = market_hours
    print(f"Market hours: {start_time_str} to {end_time_str} for {day_of_the_week}")

    # Validate and handle missing times
    if not start_time_str or not end_time_str:
        print("Market hours are invalid or incomplete.")
        return {"is_open": False}

    try:
        # Parse times in HH:MM format
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()
    except ValueError as e:
        print(f"Error parsing market times: {e}")
        return {"is_open": False}

    # Get the current time
    current_time = datetime.now(pytz.timezone('US/Eastern')).time()
    print(f"Current time: {current_time}")

    # Check if market is open
    is_open = start_time <= current_time <= end_time
    print(f"Is market open? {is_open}")

    return {"is_open": is_open}


if __name__ == '__main__':
    app.run(debug=True)


