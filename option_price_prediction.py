import streamlit as st
import plotly.express as px
from utils import prepare_stock_data
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

def display_option_price_prediction():
    st.title("Option Price Prediction")

    ticker = st.sidebar.text_input("Stock Ticker", value='AAPL')
    data = prepare_stock_data(ticker)

    X = data[['Lag1', 'Lag2']]
    y_call = data['Close']  # Using closing prices for simplicity, this should be the actual call option prices
    y_put = data['Close']  # Using closing prices for simplicity, this should be the actual put option prices

    X_train, X_test, y_call_train, y_call_test = train_test_split(X, y_call, test_size=0.2, random_state=42)
    y_put_train, y_put_test = train_test_split(y_put, test_size=0.2, random_state=42)

    model_call = LinearRegression()
    model_call.fit(X_train, y_call_train)
    call_predictions = model_call.predict(X_test)

    model_put = LinearRegression()
    model_put.fit(X_train, y_put_train)
    put_predictions = model_put.predict(X_test)

    data['Call_Predicted'] = model_call.predict(data[['Lag1', 'Lag2']])
    data['Put_Predicted'] = model_put.predict(data[['Lag1', 'Lag2']])

    st.header("Option Price Prediction")
    fig = px.line(data, x=data.index, y=['Close', 'Call_Predicted', 'Put_Predicted'], labels={'value': 'Price'}, title=f"{ticker} Option Price Prediction")
    st.plotly_chart(fig, use_container_width=True)
