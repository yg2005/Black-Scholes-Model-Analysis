import streamlit as st
import plotly.express as px
from utils import prepare_stock_data
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

def display_stock_price_prediction():
    st.title("Stock Price Prediction")

    ticker = st.sidebar.text_input("Stock Ticker", value='AAPL')
    data = prepare_stock_data(ticker)

    X = data[['Lag1', 'Lag2']]
    y = data['Return']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    data['Predicted'] = model.predict(data[['Lag1', 'Lag2']])

    st.header("Stock Price Prediction")
    fig = px.line(data, x=data.index, y=['Close', 'Predicted'], labels={'value': 'Price'}, title=f"{ticker} Stock Price Prediction")
    st.plotly_chart(fig, use_container_width=True)

