import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import norm
from datetime import datetime, timedelta, date
import requests

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
        st.warning("Failed to fetch the risk-free rate. Using default value of 5%.")
        risk_free_rate = 0.05
    return risk_free_rate

# Function to calculate the volatility of the stock
def calculate_volatility(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    hist['returns'] = hist['Close'].pct_change()
    volatility = hist['returns'].std() * np.sqrt(252)
    return volatility

# User interface with Streamlit
st.set_page_config(page_title="Real-Time Black-Scholes Options Pricing Model", layout="wide")
st.title("Real-Time Black-Scholes Options Pricing Model")

# Add a link to scroll to the user guide section
st.markdown("[Go to User Guide](#user-guide)", unsafe_allow_html=True)

# Inputs for the Black-Scholes model
st.sidebar.header("Input Parameters")
ticker = st.sidebar.text_input("Stock Ticker", value='AAPL')
S = fetch_stock_data(ticker)
st.sidebar.write(f"Current Stock Price: ${S:.2f}")

# Select expiration date
expiration_date = st.sidebar.date_input("Select Expiration Date", value=(datetime.today().date() + timedelta(days=14)))
T = (expiration_date - date.today()).days / 365  # Time to expiration in years
st.sidebar.write(f"Days to Expiration: {(expiration_date - date.today()).days} days")

# Fetch real-time risk-free rate and volatility
r = fetch_risk_free_rate()
sigma = calculate_volatility(ticker)

default_strike_price = S * 1.05  # Default strike price set to 5% above current stock price
K = st.sidebar.slider("Strike Price", min_value=1.0, max_value=2*S, value=default_strike_price)
volatility_input = st.sidebar.text_input("Volatility (%)", value=f"{sigma*100:.2f}")

# Ensure volatility is a float
try:
    sigma = float(volatility_input) / 100
except ValueError:
    st.sidebar.error("Please enter a valid volatility percentage.")
    sigma = calculate_volatility(ticker)

# Calculate option prices
call_price, put_price = black_scholes(S, K, T, r, sigma)

# Multiselect for stocks (single selection only)
stocks = ["AAPL"]
if 'stocks_list' not in st.session_state:
    st.session_state.stocks_list = stocks

selected_stock = st.selectbox("Select Stock to Display", options=st.session_state.stocks_list, index=0)

# Fetch data for the selected stock
S = fetch_stock_data(selected_stock)
sigma = calculate_volatility(selected_stock)
call_price, put_price = black_scholes(S, K, T, r, sigma)

# Display results in two columns
st.subheader(f"Stock: {selected_stock}")
col1, col2 = st.columns(2)

with col1:
    st.header("Option Prices")
    st.markdown(f"<div style='font-size:24px'><b>Call Option Price:</b> ${call_price:.2f}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:24px'><b>Put Option Price:</b> ${put_price:.2f}</div>", unsafe_allow_html=True)

with col2:
    st.header("Decision Support (not financial advice, only for education purposes)")
    st.write("Insights and recommendations based on the calculated prices.")
    # Example of simple decision support logic
    if call_price > put_price:
        st.markdown(f"<div style='font-size:24px'><b>Recommendation:</b> Buying a Call option may be more favorable.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:24px'><b>Recommendation:</b> Buying a Put option may be more favorable.</div>", unsafe_allow_html=True)

# Visualization
st.header("Market Trend Visualization")
period = st.selectbox(f"Select period for {selected_stock}", ["1mo", "3mo", "6mo", "1y", "max"], index=0)
stock_data = fetch_historical_data(selected_stock, period=period)
fig = px.line(stock_data, x=stock_data.index, y="Close", title=f"{selected_stock} Price History - {period}")
fig.update_xaxes(title="Date")
fig.update_yaxes(title="Price")
st.plotly_chart(fig, use_container_width=True)

# Allowing multiple stock inputs
st.sidebar.header("Visualize More Stocks")
stock_input = st.sidebar.text_area("Enter stock tickers separated by commas (e.g., AAPL, NVDA, AMZN)", height=50)
if st.sidebar.button("Add Stocks"):
    tickers = [ticker.strip().upper() for ticker in stock_input.split(',')]
    for stock in tickers:
        if stock not in st.session_state.stocks_list:
            st.session_state.stocks_list.append(stock)
        stock_price = fetch_stock_data(stock)
        stock_volatility = calculate_volatility(stock)
        stock_history = fetch_historical_data(stock, period="1y")
        
        st.subheader(f"{stock} Information")
        st.write(f"**Current Price:** ${stock_price:.2f}")
        st.write(f"**Volatility:** {stock_volatility:.2%}")
        
        fig = px.line(stock_history, x=stock_history.index, y="Close", title=f"{stock} Price History - 1 Year")
        fig.update_xaxes(title="Date")
        fig.update_yaxes(title="Price")
        st.plotly_chart(fig, use_container_width=True)

# Documentation and User Guide
st.header("User Guide")
st.markdown("<a id='user-guide'></a>", unsafe_allow_html=True)
st.write("""
### Black-Scholes Model
The Black-Scholes model calculates the theoretical price of European call and put options based on the following parameters:
- **S**: Current stock price
- **K**: Strike price
- **T**: Time to expiration (in years)
- **r**: Risk-free interest rate
- **sigma**: Volatility of the stock

### How to Use
1. Enter the stock ticker symbol in the sidebar.
2. Adjust the input parameters (Strike Price, Time to Expiration, Risk-Free Rate, Volatility).
3. View the calculated option prices and decision support recommendations.
4. Check the market trend visualization for the selected stock.
5. Add multiple stock tickers in the sidebar to visualize their information.
""")
