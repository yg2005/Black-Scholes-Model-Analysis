import streamlit as st
import plotly.express as px
from utils import prepare_trading_data
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def display_trading_signal_generation():
    st.title("Trading Signal Generation")

    ticker = st.sidebar.text_input("Stock Ticker", value='AAPL')
    data = prepare_trading_data(ticker)

    X = data[['Return', 'MA10', 'MA50', 'RSI']]
    y = data['Signal']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    data['Signal_Predicted'] = model.predict(data[['Return', 'MA10', 'MA50', 'RSI']])

    st.header("Trading Signal Generation")
    fig = px.line(data, x=data.index, y=['Close', 'Signal_Predicted'], labels={'value': 'Price'}, title=f"{ticker} Trading Signal Generation")
    st.plotly_chart(fig, use_container_width=True)
