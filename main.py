import streamlit as st
from black_scholes import display_black_scholes_model
from stock_price_prediction import display_stock_price_prediction
from option_price_prediction import display_option_price_prediction
from trading_signal_generation import display_trading_signal_generation

# Main application
st.set_page_config(page_title="Real-Time Stock Analysis", layout="wide")

# Page navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Black-Scholes Model", "Stock Price Prediction", "Option Price Prediction", "Trading Signal Generation"])

if page == "Black-Scholes Model":
    display_black_scholes_model()
elif page == "Stock Price Prediction":
    display_stock_price_prediction()
elif page == "Option Price Prediction":
    display_option_price_prediction()
elif page == "Trading Signal Generation":
    display_trading_signal_generation()
