ClimCoin: The Green Investment Platform

Welcome to ClimCoin, a cryptocurrency platform designed to optimize stock portfolios for maximum profit while promoting sustainable and responsible investing. Users are rewarded with ClimCoins for investing in companies with high ESG (Environmental, Social, and Governance) scores.

Features

User Authentication
Secure Registration and Login: Using bcrypt for password hashing to ensure user data security.
Portfolio Management
Buy and Sell Stocks: Track user portfolios in a SQLite database.
ESG Score Integration
Real-Time ESG Scores and Stock Prices: Fetches and displays ESG scores and stock prices from Yahoo Finance.
Historical Data Analysis
Plot and Predict Stock Prices: Uses polynomial regression to plot historical stock prices and predict future prices.
ClimCoin Rewards
Earn Rewards: Calculates and awards ClimCoins based on ESG scores and the number of stocks owned.
Membership Tiers
Tiered Membership: Users are categorized into tiers (Starter, Bronze, Silver, Gold) based on their ClimCoin balance.
Technologies Used

Python: Core programming language for backend logic.
Flask: Web framework for creating the platform.
SQLite: Database for storing user and portfolio information.
bcrypt: Library for secure password hashing.
aiohttp & asyncio: Libraries for asynchronous HTTP requests.
YahooFinancials & YahooQuery: APIs for fetching financial data.
Matplotlib & Pandas: Libraries for data analysis and visualization.
HTML & CSS: Frontend for the user interface.
Functions

User Functions
register_user(username, password): Registers a new user.
authenticate_user(username, password): Authenticates an existing user.
Financial Data Functions
fetch_esg_and_price(ticker, session): Asynchronously fetches ESG scores and stock prices.
fetch_historical_data(ticker, start_date, end_date): Fetches historical stock data.
plot_and_predict_historical_data(prices, ticker): Plots and predicts stock prices using polynomial regression.
ClimCoin Functions
calculate_climcoins(esg_score, number_of_stocks): Calculates ClimCoins based on ESG scores and stock quantity.
update_climcoins_and_tier(username, ticker, number_of_stocks): Updates user's ClimCoins and membership tier.
Portfolio Management Functions
show_portfolio(username, portfolio): Displays the user's portfolio and ClimCoin balance.
update_portfolio(username, portfolio, action, stock_info, price): Updates the user's portfolio.
Contribution

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

Example Usage

Here’s a quick guide on how to use ClimCoin:

Initialize the Database: Run init_db() to set up the database.
Register and Authenticate Users:
Register a new user with register_user("username", "password").
Authenticate an existing user with authenticate_user("username", "password").
Fetch ESG Scores and Prices:
Use asyncio.run(fetch_selected_esg_and_prices(["AAPL", "MSFT"])) to get ESG scores and prices for selected tickers.
Fetch and Plot Historical Data:
Fetch historical data with fetch_historical_data("AAPL", "2023-01-01", "2023-12-31").
Plot and predict stock prices with plot_and_predict_historical_data(prices, "AAPL").
Manage Portfolios:
Update and show portfolios with update_portfolio("username", portfolio, "buy", stock_info, price) and show_portfolio("username", portfolio).
