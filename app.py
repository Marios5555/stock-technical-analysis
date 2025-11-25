import yfinance as yf
import streamlit as st
import datetime
import talib as ta
import pandas as pd

st.set_page_config(page_title="Technical Analysis Dashboard", layout="wide")

st.write("""
# 📈 Stock Technical Analysis Dashboard
Analyze any stock with Moving Averages, Bollinger Bands, MACD, RSI, CCI, and OBV!
""")

st.sidebar.header("📊 User Input Parameters")
today = datetime.date.today()

ticker = st.sidebar.text_input("Stock Ticker", "AAPL")
start_date = st.sidebar.text_input("Start Date", "2024-01-01")
end_date = st.sidebar.text_input("End Date", str(today))

start = pd.to_datetime(start_date)
end = pd.to_datetime(end_date)

try:
    with st.spinner(f'📥 Loading data for {ticker}...'):
        data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
    
    if data.empty:
        st.error(f"❌ No data found for {ticker}. Please check the ticker symbol.")
    else:
        price_col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
        
        # Current price display
        current_price = data[price_col].iloc[-1]
        prev_price = data[price_col].iloc[-2]
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label=f"{ticker} Current Price", 
                value=f"${current_price:.2f}",
                delta=f"{price_change_pct:.2f}%"
            )
        
        # Calculate all indicators
        data["SMA_20"] = ta.SMA(data[price_col].values, timeperiod=20)
        data["EMA_20"] = ta.EMA(data[price_col].values, timeperiod=20)
        data["BB_upper"], data["BB_middle"], data["BB_lower"] = ta.BBANDS(
            data[price_col].values, timeperiod=20
        )
        data["MACD"], data["MACD_signal"], data["MACD_hist"] = ta.MACD(
            data[price_col].values, fastperiod=12, slowperiod=26, signalperiod=9
        )
        data["CCI"] = ta.CCI(
            data["High"].values, data["Low"].values, data["Close"].values, timeperiod=14
        )
        data["RSI"] = ta.RSI(data[price_col].values, timeperiod=14)
        data["OBV"] = ta.OBV(
            data[price_col].values.astype(float), 
            data["Volume"].values.astype(float)
        ) / 10**6
        
        # Display charts
        st.header(f"💰 Price Chart - {ticker}")
        st.line_chart(data[price_col])
        
        st.header(f"📈 Moving Averages - {ticker}")
        st.line_chart(data[[price_col, "SMA_20", "EMA_20"]])
        
        st.header(f"📊 Bollinger Bands - {ticker}")
        st.line_chart(data[[price_col, "BB_upper", "BB_middle", "BB_lower"]])
        
        st.header(f"📉 MACD - {ticker}")
        st.line_chart(data[["MACD", "MACD_signal"]])
        
        st.header(f"🎯 Relative Strength Index (RSI) - {ticker}")
        st.line_chart(data["RSI"])
        
        st.header(f"📍 Commodity Channel Index (CCI) - {ticker}")
        st.line_chart(data["CCI"])
        
        st.header(f"📦 On Balance Volume (Millions) - {ticker}")
        st.line_chart(data["OBV"])
        
        # Latest indicator values
        st.header("📋 Latest Indicator Values")
        col1, col2, col3 = st.columns(3)
        
        latest_rsi = data['RSI'].iloc[-1]
        latest_cci = data['CCI'].iloc[-1]
        latest_macd = data['MACD'].iloc[-1]
        latest_signal = data['MACD_signal'].iloc[-1]
        
        with col1:
            st.metric("RSI (14)", f"{latest_rsi:.2f}")
            if latest_rsi > 70:
                st.caption("🔴 Overbought")
            elif latest_rsi < 30:
                st.caption("🟢 Oversold")
            else:
                st.caption("⚪ Neutral")
            
            st.metric("SMA (20)", f"${data['SMA_20'].iloc[-1]:.2f}")
        
        with col2:
            st.metric("MACD", f"{latest_macd:.2f}")
            if latest_macd > latest_signal:
                st.caption("🟢 Bullish Signal")
            else:
                st.caption("🔴 Bearish Signal")
            
            st.metric("EMA (20)", f"${data['EMA_20'].iloc[-1]:.2f}")
        
        with col3:
            st.metric("CCI (14)", f"{latest_cci:.2f}")
            if latest_cci > 100:
                st.caption("🔴 Overbought")
            elif latest_cci < -100:
                st.caption("🟢 Oversold")
            else:
                st.caption("⚪ Neutral")
            
            st.metric("OBV (M)", f"{data['OBV'].iloc[-1]:.2f}")
        
        # Download data option
        st.header("💾 Download Data")
        csv = data.to_csv()
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{ticker}_technical_analysis.csv",
            mime="text/csv"
        )
        
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    st.info("💡 Make sure you entered a valid ticker symbol and date range.")
