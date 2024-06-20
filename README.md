ClimCoin

ClimCoin is a cryptocurrency platform designed to optimize stock portfolios for maximum profit while promoting sustainable and responsible investing. Users are rewarded with ClimCoins for investing in companies with high ESG (Environmental, Social, and Governance) scores.

Features

User Authentication: Secure registration and login using bcrypt.
Portfolio Management: Users can buy and sell stocks, and their portfolios are tracked in a SQLite database.
ESG Score Integration: Fetches and displays ESG scores and stock prices from Yahoo Finance.
Historical Data Analysis: Plots historical stock prices and predicts future prices using polynomial regression.
ClimCoin Rewards: Calculates and awards ClimCoins based on ESG scores and the number of stocks owned.
Membership Tiers: Users are categorized into tiers (Starter, Bronze, Silver, Gold) based on their ClimCoin balance.
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
register_user(username, password): Registers a new user.
authenticate_user(username, password): Authenticates an existing user.
fetch_esg_and_price(ticker, session): Asynchronously fetches ESG scores and stock prices.
fetch_historical_data(ticker, start_date, end_date): Fetches historical stock data.
plot_and_predict_historical_data(prices, ticker): Plots and predicts stock prices using polynomial regression.
calculate_climcoins(esg_score, number_of_stocks): Calculates ClimCoins based on ESG scores and stock quantity.
update_climcoins_and_tier(username, ticker, number_of_stocks): Updates user's ClimCoins and membership tier.
show_portfolio(username, portfolio): Displays the user's portfolio and ClimCoin balance.

Contribution

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.
