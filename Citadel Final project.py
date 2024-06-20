import sqlite3
import bcrypt
import asyncio
import aiohttp
from yahooquery import Ticker
from yahoofinancials import YahooFinancials
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate
from termcolor import colored
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np
import warnings

warnings.filterwarnings("ignore", message="X does not have valid feature names")

# Initialize the database connection with ClimCoins and Tier
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Create the users table with the new schema including climcoins and tier columns if they do not exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, climcoins REAL, tier TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS portfolios (username TEXT, ticker TEXT, shares INTEGER, PRIMARY KEY (username, ticker))''')
    conn.commit()
    conn.close()

# Function to register a new user
def register_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, climcoins, tier) VALUES (?, ?, ?, ?)", (username, hashed_password, 0.0, "Starter"))
        conn.commit()
    except sqlite3.IntegrityError:
        print(colored("Username already exists!", 'red'))
        return False
    conn.close()
    return True

# Function to authenticate a user
def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        return True
    else:
        return False

# Asynchronous function to fetch ESG scores and stock prices
async def fetch_esg_and_price(ticker, session):
    ticker_obj = Ticker(ticker)
    esg_scores = ticker_obj.esg_scores.get(ticker, {})
    financials = YahooFinancials(ticker)
    current_price = financials.get_current_price()

    return [
        ticker,
        f"${current_price:.2f}",
        esg_scores.get('totalEsg', 'N/A'),
        esg_scores.get('environmentScore', 'N/A'),
        esg_scores.get('socialScore', 'N/A'),
        esg_scores.get('governanceScore', 'N/A')
    ]

# Function to fetch ESG scores and stock prices for selected tickers
async def fetch_selected_esg_and_prices(tickers):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_esg_and_price(ticker, session) for ticker in tickers]
        esg_data = await asyncio.gather(*tasks)
        
        headers = ["Ticker", "Current Price", "Total ESG Score", "Environmental Score", "Social Score", "Governance Score"]
        print("\n" + colored("💡 ESG Scores and Stock Prices 💡", 'cyan', attrs=['bold', 'underline']))
        print(tabulate(esg_data, headers=headers, tablefmt="fancy_grid"))

# Function to fetch historical price data for a period 
def fetch_historical_data(ticker_symbol, start_date, end_date):
    ticker = YahooFinancials(ticker_symbol)
    data = ticker.get_historical_price_data(start_date, end_date, "daily")
    return data[ticker_symbol]["prices"]

# Function to plot historical data and predict future price using polynomial regression
def plot_and_predict_historical_data(prices, ticker):
    df = pd.DataFrame(prices)
    df['formatted_date'] = pd.to_datetime(df['formatted_date'])
    df.set_index('formatted_date', inplace=True)

    # Calculate moving averages
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()

    # Plot historical data
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['close'], label='Close Price', color='green', linestyle='-', marker='o')
    plt.plot(df.index, df['MA20'], label='20-Day MA', color='blue', linestyle='--')
    plt.plot(df.index, df['MA50'], label='50-Day MA', color='red', linestyle='--')

    # Polynomial regression for prediction
    df.reset_index(inplace=True)
    df['timestamp'] = df['formatted_date'].map(pd.Timestamp.timestamp)
    X = df[['timestamp']]
    y = df['close']
    
    poly = PolynomialFeatures(degree=3)
    X_poly = poly.fit_transform(X)
    
    model = LinearRegression()
    model.fit(X_poly, y)
    df['predicted'] = model.predict(X_poly)

    # Predict future price (10 days ahead)
    future_dates = pd.date_range(start=df['formatted_date'].max(), periods=11, freq='B')[1:]
    future_timestamps = future_dates.map(pd.Timestamp.timestamp).values.reshape(-1, 1)
    future_timestamps_poly = poly.transform(future_timestamps)
    future_predictions = model.predict(future_timestamps_poly)
    
    future_df = pd.DataFrame({'formatted_date': future_dates, 'predicted': future_predictions})
    df = pd.concat([df, future_df], ignore_index=True)

    plt.plot(df['formatted_date'], df['predicted'], label='Predicted Price', color='orange', linestyle='--')

    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Price ($)', fontsize=14)
    plt.title(f'Historical and Predicted Stock Prices for {ticker}', fontsize=18, fontweight='bold')
    plt.legend()
    plt.grid(True)
    plt.savefig('historical_prices.png')
    plt.show()

    analyze_graph(df, ticker, future_df)

# Function to analyze the graph data
def analyze_graph(df, ticker, future_df):
    highest_price = df['close'].max()
    lowest_price = df['close'].min()

    print("\n" + colored(f"🔍 Analysis of {ticker} Stock Prices 🔍", 'cyan', attrs=['bold', 'underline']))
    print(f"📊 {colored('Highest Price:', 'yellow')} ${highest_price:.2f}")
    print(f"📉 {colored('Lowest Price:', 'yellow')} ${lowest_price:.2f}")

    recent_trend = "📈 Uptrend" if df['close'].iloc[-1] > df['close'].iloc[-5] else "📉 Downtrend"
    print(f"{colored('Recent Trend:', 'yellow')} {recent_trend}")

    golden_cross = (df['MA20'].iloc[-1] > df['MA50'].iloc[-1]) and (df['MA20'].iloc[-2] < df['MA50'].iloc[-2])
    death_cross = (df['MA20'].iloc[-1] < df['MA50'].iloc[-1]) and (df['MA20'].iloc[-2] > df['MA50'].iloc[-2])

    if golden_cross:
        print(colored("🌟 Golden Cross detected: A potential bullish signal.", 'green'))
    elif death_cross:
        print(colored("🔴 Death Cross detected: A potential bearish signal.", 'red'))
    else:
        print(colored("No significant cross detected between moving averages.", 'white'))

    # Future prediction analysis
    future_price_str = ', '.join([f"{row['formatted_date'].date()}: ${row['predicted']:.2f}" for idx, row in future_df.iterrows()])
    print(f"\n📅 {colored('Predicted prices for the next 10 business days:', 'yellow')} {future_price_str}")

# Function to provide detailed analysis
def provide_detailed_analysis(ticker, model):
    coef = model.coef_[0]
    intercept = model.intercept_
    trend = "upward" if coef > 0 else "downward"

    analysis = (
        f"\n📊 {colored('Detailed Polynomial Regression Analysis for', 'cyan')} {ticker} 📉\n"
        f"The polynomial regression model predicts future stock prices based on the historical data. The trend is modeled as a polynomial relationship between time and price. "
        f"The coefficient (slope) of the regression line is {coef:.2f}, which indicates an {trend} trend. "
        f"The intercept of the model is {intercept:.2f}, which represents the starting point of the trend line on the price axis.\n\n"
        "The model's predictions provide an insight into how the stock price is expected to change in the near future. "
        "However, it's essential to consider other factors such as market conditions, company performance, and broader economic indicators "
        "that might influence stock prices beyond historical trends. This analysis helps investors make informed decisions by understanding "
        "the underlying trend and potential future movements of the stock price."
    )
    print(colored(analysis, 'magenta'))

# Function to get stock information
def get_stock_info():
    stock_info = {}
    stock_info['ticker'] = input("Enter the company ticker symbol: ").upper()
    stock_info['number_of_stocks'] = int(input("Enter the number of stocks: "))
    return stock_info

# Function to calculate ClimCoins based on ESG score and number of stocks
def calculate_climcoins(esg_score, number_of_stocks):
    # Example formula: ESG Score * Number of Stocks
    return esg_score * number_of_stocks

def determine_tier(climcoins):
    if climcoins >= 1000:
        return "Gold"
    elif climcoins >= 500:
        return "Silver"
    elif climcoins >= 100:
        return "Bronze"
    else:
        return "Starter"

# Function to update ClimCoins and Tier
def update_climcoins_and_tier(username, ticker, number_of_stocks):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Fetch the ESG score for the ticker
    ticker_obj = Ticker(ticker)
    esg_scores = ticker_obj.esg_scores.get(ticker, {})
    total_esg_score = esg_scores.get('totalEsg', 0)

    # Calculate ClimCoins
    climcoins_earned = calculate_climcoins(total_esg_score, number_of_stocks)

    # Update ClimCoins and determine tier
    c.execute("SELECT climcoins FROM users WHERE username = ?", (username,))
    current_climcoins = c.fetchone()[0]
    new_climcoins = current_climcoins + climcoins_earned

    # Determine new tier
    new_tier = determine_tier(new_climcoins)

    c.execute("UPDATE users SET climcoins = ?, tier = ? WHERE username = ?", (new_climcoins, new_tier, username))
    conn.commit()
    conn.close()

    return new_climcoins, new_tier

# Function to update and show portfolio
def update_portfolio(username, portfolio, action, stock_info, price):
    ticker = stock_info['ticker']
    number_of_stocks = stock_info['number_of_stocks']

    if ticker not in portfolio:
        portfolio[ticker] = 0

    if action == 'buy':
        portfolio[ticker] += number_of_stocks
    elif action == 'sell':
        portfolio[ticker] = max(0, portfolio[ticker] - number_of_stocks)

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    for ticker, shares in portfolio.items():
        c.execute("REPLACE INTO portfolios (username, ticker, shares) VALUES (?, ?, ?)", (username, ticker, shares))
    conn.commit()
    conn.close()

    climcoins, tier = update_climcoins_and_tier(username, ticker, number_of_stocks)

    return portfolio, climcoins, tier

def load_portfolio(username):
    portfolio = {}
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT ticker, shares FROM portfolios WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    for row in rows:
        portfolio[row[0]] = row[1]
    return portfolio

def show_portfolio(username, portfolio):
    portfolio_data = [[ticker, shares] for ticker, shares in portfolio.items()]
    headers = ["Ticker", "Shares"]
    print("\n" + colored("📈 Current Portfolio 📉", 'cyan', attrs=['bold', 'underline']))
    print(tabulate(portfolio_data, headers=headers, tablefmt="fancy_grid"))

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT climcoins, tier FROM users WHERE username = ?", (username,))
    user_data = c.fetchone()
    conn.close()
    climcoins, tier = user_data
    print(f"\n{colored('ClimCoins:', 'green', attrs=['bold'])} {climcoins}")
    print(f"{colored('Membership Tier:', 'green', attrs=['bold'])} {tier}")

def main():
    init_db()
    print(colored("💚 Welcome to the Green Investment Platform! 💚", 'green', attrs=['bold', 'underline']))

    choice = input("Are you a new user? (yes/no): ").strip().lower()
    if choice == 'yes':
        username = input("Create a username: ").strip()
        password = input("Create a password: ").strip()
        if register_user(username, password):
            print(colored("User registered successfully!", 'green'))
        else:
            return
    else:
        username = input("Enter your username: ").strip()
        password = input("Enter your password: ").strip()
        if authenticate_user(username, password):
            print(colored("User authenticated successfully!", 'green'))
        else:
            print(colored("Invalid username or password!", 'red'))
            return

    # List of top 100 most sustainable companies' tickers
    tickers = [
        'AAPL', 'MSFT', 'TSLA', 'NVDA', 'GOOGL', 'ADBE', 'AMZN', 'NFLX', 'INTC', 'CSCO', 
        'PEP', 'QCOM', 'HON', 'BA', 'SBUX', 'ORCL', 'IBM', 'CRM', 'PYPL', 'GILD',
        'TXN', 'AVGO', 'AMGN', 'AMD', 'ADI', 'INTU', 'VRTX', 'MU', 'BKNG', 'MCHP',
        'SWKS', 'LRCX', 'KLAC', 'CDNS', 'SNPS', 'XLNX', 'IDXX', 'ASML', 'MRVL', 'ANSS',
        'MTCH', 'WDAY', 'OKTA', 'TEAM', 'ZS', 'NOW', 'PINS', 'TTD', 'ZM', 'CRWD',
        'DOCU', 'FSLY', 'DDOG', 'FVRR', 'NET', 'SHOP', 'SPOT', 'SQ', 'TWLO', 'UBER',
        'LYFT', 'ABNB', 'ROKU', 'SNAP', 'BIDU', 'NTES', 'JD', 'PDD', 'BABA', 'VIPS',
        'SPCE', 'PLTR', 'U', 'NVTA', 'BNTX', 'MRNA', 'TWST', 'PACB', 'CRSP', 'NTLA',
        'EDIT', 'VRTX', 'REGN', 'DXCM', 'TDOC', 'ISRG', 'SYK', 'EW', 'ABT', 'ILMN',
        'RMD', 'STE', 'ALGN', 'TFX', 'ZBH', 'DHR', 'BSX', 'BAX', 'BHC', 'WST'
    ]

    # Display the tickers
    print("\n" + colored("Top 100 Most Sustainable Companies:", 'cyan', attrs=['bold', 'underline']))
    print(', '.join(tickers))

    # Prompt user to input tickers they are interested in
    selected_tickers = input("\nEnter the ticker symbols you are interested in (comma-separated): ").upper().split(',')

    asyncio.run(fetch_selected_esg_and_prices(selected_tickers))

    portfolio = load_portfolio(username)

    stock_info = get_stock_info()

    show_historical = input("Do you want to see historical price data for a period? (yes/no): ").lower()
    if show_historical == "yes":
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        historical_data = fetch_historical_data(stock_info['ticker'], start_date, end_date)
        plot_and_predict_historical_data(historical_data, stock_info['ticker'])

    action = input("After seeing all of this information and the graph, would you like to buy or sell? ").lower()
    if action not in ['buy', 'sell']:
        print(colored("Invalid action! Please enter 'buy' or 'sell'.", 'red'))
        return
    price = YahooFinancials(stock_info['ticker']).get_current_price()
    portfolio, climcoins, tier = update_portfolio(username, portfolio, action, stock_info, price)

    show_portfolio(username, portfolio)

if __name__ == "__main__":
    main()
