import requests
from Core.stockValue import get_stock_price
from Core.Exceptions import *

SERVICES = {
    "stocks1": "http://stocks1-a:8000/stocks",
    "stocks2": "http://stocks2:8000/stocks"
}

def get_stocks_with_filter(query_params: dict = {}) -> dict:
 
    # Determine which services to query
    portfolios = query_params.get("portfolio")
    if not portfolios:
        portfolios = list(SERVICES.keys())
    else:
        portfolios = list([portfolios])

    stocks = {}

    # Query each service
    for portfolio in portfolios:
        if portfolio not in SERVICES:
            raise InvalidQueryParameterError(f"Invalid portfolio: {portfolio}")
        service_url = SERVICES.get(portfolio)
        try:
            response = requests.get(service_url)
            response.raise_for_status()
            stocks_list = response.json()
            if isinstance(stocks_list, list):
                for stock in stocks_list:
                    stocks[stock["symbol"]] = stock
            else:
                print(f"Unexpected response format from {portfolio}: {stocks_list}")
        except Exception as e:
            print(f"Failed to fetch stocks from {portfolio}: {e}")

    # Filter stocks based on the number of shares
    try:
            min_amount_of_shares = float(query_params.get("numsharesgt", float('-inf')))
    except ValueError:
            # min_amount_of_shares = float('-inf')  # Use -infinity if invalid value
            raise InvalidQueryParameterError("Invalid number of shares")
    try:
            max_amount_of_shares = float(query_params.get("numshareslt", float('inf')))
    except ValueError:
            raise InvalidQueryParameterError("Invalid number of shares")
            # max_amount_of_shares = float('inf')  # Use +infinity if invalid value
    
    filtered_stocks = {}
    for stock_id, stock_data in stocks.items():
        shares = stock_data.get("shares")
        if shares is not None and isinstance(shares, (int, float)):
            if min_amount_of_shares < shares < max_amount_of_shares:
                filtered_stocks[stock_id] = stock_data

    return filtered_stocks

def get_capital_gains(query_params):

    total_capital_gains = 0
    stocks_portfolio = get_stocks_with_filter(query_params)

    for stock in stocks_portfolio.values():
        current_price = get_stock_price(stock["symbol"])
        stock_capital_gain = current_price - stock["purchase price"]
        total_stock_capital_gain = stock["shares"] * stock_capital_gain
        total_capital_gains += total_stock_capital_gain
    
    total_capital_gains = round(total_capital_gains, 2)   
    return total_capital_gains