"""Enhanced features for the crypto dashboard."""

import time
from typing import List, Optional
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore


def create_portfolio_tracker() -> None:
    """Create a simple portfolio tracking section."""
    st.header("💼 Portfolio Tracker")
    
    # Initialize portfolio in session state
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add Holdings")
        symbol = st.selectbox("Select Crypto", options=["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"])
        amount = st.number_input("Amount Held", min_value=0.0, step=0.001, format="%.6f")
        buy_price = st.number_input("Average Buy Price ($)", min_value=0.0, step=0.01)
        
        if st.button("Add to Portfolio"):
            if amount > 0 and buy_price > 0:
                st.session_state.portfolio[symbol] = {  # type: ignore
                    'amount': amount,
                    'buy_price': buy_price,
                    'timestamp': time.time()
                }
                st.success(f"Added {amount} {symbol.replace('USDT', '')} to portfolio!")
    
    with col2:
        st.subheader("Current Holdings")
        if st.session_state.portfolio:  # type: ignore
            for symbol, holding in st.session_state.portfolio.items():  # type: ignore
                crypto_name = str(symbol).replace('USDT', '')  # type: ignore
                st.write(f"**{crypto_name}**: {holding['amount']:.6f}")  # type: ignore
                st.write(f"Avg Buy Price: ${holding['buy_price']:.2f}")  # type: ignore
                
                # Calculate P&L (would need current price)
                st.write("---")
        else:
            st.info("No holdings added yet")


def create_technical_indicators(prices: List[float], timestamps: List[float]) -> Optional[go.Figure]:  # type: ignore
    """Create advanced chart with technical indicators."""
    if len(prices) < 20:
        return None
    
    # Calculate simple moving averages
    sma_20: List[Optional[float]] = []
    sma_50: List[Optional[float]] = []
    
    for i in range(len(prices)):
        if i >= 19:
            sma_20.append(sum(prices[i-19:i+1]) / 20)
        else:
            sma_20.append(None)
        
        if i >= 49:
            sma_50.append(sum(prices[i-49:i+1]) / 50)
        else:
            sma_50.append(None)
    
    # Create subplot
    fig = make_subplots(  # type: ignore
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price with Moving Averages', 'Volume'),
        vertical_spacing=0.1
    )
    
    # Convert timestamps to datetime
    from datetime import datetime
    datetimes = [datetime.fromtimestamp(ts) for ts in timestamps]
    
    # Price line
    fig.add_trace(  # type: ignore
        go.Scatter(x=datetimes, y=prices, name="Price", line=dict(color="#1f77b4", width=2)),  # type: ignore
        row=1, col=1
    )
    
    # Moving averages
    fig.add_trace(  # type: ignore
        go.Scatter(x=datetimes, y=sma_20, name="SMA 20", line=dict(color="#ff7f0e", width=1)),  # type: ignore
        row=1, col=1
    )
    
    if any(x is not None for x in sma_50):
        fig.add_trace(  # type: ignore
            go.Scatter(x=datetimes, y=sma_50, name="SMA 50", line=dict(color="#2ca02c", width=1)),  # type: ignore
            row=1, col=1
        )
    
    # Volume bars (simulated)
    volumes = [abs(prices[i] - prices[i-1]) * 1000 if i > 0 else 0 for i in range(len(prices))]
    fig.add_trace(  # type: ignore
        go.Bar(x=datetimes, y=volumes, name="Volume", marker_color="#d62728"),  # type: ignore
        row=2, col=1
    )
    
    fig.update_layout(  # type: ignore
        title="Advanced Technical Analysis",
        height=600,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    return fig


def create_market_heatmap(df: pd.DataFrame) -> Optional[go.Figure]:  # type: ignore
    """Create a market heatmap showing price changes."""
    if df.empty or len(df) < 5:
        return None
    
    # Prepare data for heatmap
    symbols = [s.replace('USDT', '') for s in df['symbol'].head(20)]
    
    # Try different column names for price change (handle normalized columns)
    if 'pricechangepercent' in df.columns:
        changes = df['pricechangepercent'].head(20).tolist()
    elif 'priceChangePercent' in df.columns:
        changes = df['priceChangePercent'].head(20).tolist()
    elif 'price_change_percent' in df.columns:
        changes = df['price_change_percent'].head(20).tolist()
    elif 'change' in df.columns:
        changes = df['change'].head(20).tolist()
    else:
        # Fallback to zeros if no price change column found
        changes = [0.0] * len(symbols)
    
    # Create visualization (removed unused colors variable)
    fig = go.Figure(data=go.Scatter(  # type: ignore
        x=list(range(len(symbols))),
        y=[1] * len(symbols),
        mode='markers',
        marker=dict(
            size=[abs(x) * 5 + 20 for x in changes],
            color=changes,
            colorscale='RdYlGn',
            colorbar=dict(title="Price Change %"),
            showscale=True
        ),
        text=[f"{s}<br>{c:.2f}%" for s, c in zip(symbols, changes)],
        textposition="middle center",
        hovertemplate="<b>%{text}</b><extra></extra>"
    ))
    
    fig.update_layout(  # type: ignore
        title="Market Heatmap - 24h Price Changes",
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        height=300,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig


def create_alert_history() -> None:
    """Create alert history tracking."""
    st.header("🔔 Alert History")
    
    # Initialize alert history
    if 'alert_history' not in st.session_state:
        st.session_state.alert_history = []
    
    # Display recent alerts
    if st.session_state.alert_history:  # type: ignore
        for alert in st.session_state.alert_history[-10:]:  # type: ignore # Show last 10 alerts
            alert_time = time.strftime("%H:%M:%S", time.localtime(float(alert['timestamp'])))  # type: ignore
            if alert['type'] == 'price':  # type: ignore
                st.info(f"🕐 {alert_time} - {alert['message']}")  # type: ignore
            else:
                st.warning(f"🕐 {alert_time} - {alert['message']}")  # type: ignore
    else:
        st.info("No alerts triggered yet")
    
    # Clear history button
    if st.button("Clear Alert History"):
        st.session_state.alert_history = []  # type: ignore
        st.success("Alert history cleared!")


def add_alert_to_history(message: str, alert_type: str) -> None:
    """Add an alert to the history."""
    if 'alert_history' not in st.session_state:
        st.session_state.alert_history = []  # type: ignore
    
    alert = {  # type: ignore
        'timestamp': time.time(),
        'message': message,
        'type': alert_type
    }
    
    st.session_state.alert_history.append(alert)  # type: ignore
    
    # Keep only last 50 alerts
    if len(st.session_state.alert_history) > 50:  # type: ignore
        st.session_state.alert_history = st.session_state.alert_history[-50:]  # type: ignore


def create_price_comparison() -> None:
    """Create multi-symbol price comparison chart."""
    st.header("📊 Price Comparison")
    
    symbols = st.multiselect(
        "Select symbols to compare",
        options=["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT", "LINKUSDT"],
        default=["BTCUSDT", "ETHUSDT"]
    )
    
    if len(symbols) >= 2:
        st.info(f"Comparing {len(symbols)} cryptocurrencies")
        # This would require multiple WebSocket connections
        # For now, show a placeholder
        fig = go.Figure()  # type: ignore
        for symbol in symbols:
            # Simulate some data
            import random
            x_data = list(range(100))
            y_data = [100 + random.uniform(-5, 5) * j for j in range(100)]
            
            fig.add_trace(go.Scatter(  # type: ignore
                x=x_data,
                y=y_data,
                name=symbol.replace('USDT', ''),
                mode='lines'
            ))
        
        fig.update_layout(  # type: ignore
            title="Price Comparison (Normalized)",
            xaxis_title="Time",
            yaxis_title="Price Index",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)  # type: ignore


def create_news_feed() -> None:
    """Create a crypto news feed section."""
    st.header("📰 Crypto News")
    
    # Mock news data (in real app, would fetch from news API)
    news_items = [
        {
            "title": "Bitcoin Reaches New Support Level",
            "time": "2 hours ago",
            "summary": "BTC finds strong support at key technical level..."
        },
        {
            "title": "Ethereum Network Upgrade Complete",
            "time": "4 hours ago", 
            "summary": "Latest upgrade improves transaction speeds..."
        },
        {
            "title": "Altcoin Season Predictions",
            "time": "6 hours ago",
            "summary": "Analysts predict potential altcoin momentum..."
        }
    ]
    
    for news in news_items:
        with st.expander(f"📄 {news['title']} - {news['time']}"):
            st.write(news['summary'])


def create_export_features() -> None:
    """Create data export functionality."""
    st.header("💾 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Portfolio"):
            if 'portfolio' in st.session_state and st.session_state.portfolio:  # type: ignore
                portfolio_df = pd.DataFrame(st.session_state.portfolio).T  # type: ignore
                csv = portfolio_df.to_csv()
                st.download_button(
                    label="Download Portfolio CSV",
                    data=csv,
                    file_name=f"crypto_portfolio_{int(time.time())}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No portfolio data to export")
    
    with col2:
        if st.button("Export Alert History"):
            if 'alert_history' in st.session_state and st.session_state.alert_history:  # type: ignore
                alerts_df = pd.DataFrame(st.session_state.alert_history)  # type: ignore
                csv = alerts_df.to_csv()
                st.download_button(
                    label="Download Alerts CSV",
                    data=csv,
                    file_name=f"crypto_alerts_{int(time.time())}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No alert history to export")
