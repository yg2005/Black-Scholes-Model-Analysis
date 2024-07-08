import yfinance as yf
import numpy as np
import requests
from scipy.stats import norm

# Function to calculate d1 and d2 for Black-Scholes formula
def calculate_d1_d2(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2

# Function to calculate Black-Scholes call and put option prices
def black_scholes(S, K, T, r, sigma):
    d1, d2 = calculate_d1_d2(S, K, T, r, sigma)
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return call_price, put_price

# Function to fetch real-time stock data
def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    return data['Close'].iloc[-1]

# Function to fetch historical stock data
def fetch_historical_data(ticker, period="1mo"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

# Function to fetch the risk-free rate (using 1-year Treasury yield from a financial API)
def fetch_risk_free_rate():
    try:
        response = requests.get("https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=monthly&maturity=1year&apikey=YOUR_API_KEY")
        data = response.json()
        risk_free_rate = float(data['data'][-1]['value']) / 100  # Convert percentage to decimal
    except Exception as e:
        risk_free_rate = 0.05
    return risk_free_rate

# Function to calculate the volatility of the stock
def calculate_volatility(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    hist['returns'] = hist['Close'].pct_change()
    volatility = hist['returns'].std() * np.sqrt(252)
    return volatility

# Function to prepare data for stock price prediction
def prepare_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="5y")
    data['Return'] = data['Close'].pct_change()
    data['Lag1'] = data['Return'].shift(1)
    data['Lag2'] = data['Return'].shift(2)
    data.dropna(inplace=True)
    return data

# Function to prepare data for trading signal generation
def prepare_trading_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="5y")
    data['Return'] = data['Close'].pct_change()
    data['MA10'] = data['Close'].rolling(window=10).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['RSI'] = (data['Close'].diff(1) > 0).rolling(window=14).sum() / 14 * 100
    data['Signal'] = np.where(data['MA10'] > data['MA50'], 1, 0)
    data.dropna(inplace=True)
    return data
