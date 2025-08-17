"""UI components for the Streamlit crypto dashboard."""

from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go  # type: ignore
import streamlit as st

try:
    from utils import (
        clean_symbol_name,
        format_percentage,
        format_price,
        format_volume,
        get_color_for_change,
    )
except ImportError:
    # Fallback functions if utils import fails
    def clean_symbol_name(symbol: str) -> str:
        return str(symbol).replace('USDT', '').replace('BTC', '').replace('ETH', '')
    
    def format_percentage(percentage: Any) -> str:
        try:
            return f"{float(percentage):.2f}%" if percentage else "0.00%"
        except (ValueError, TypeError):
            return "0.00%"
    
    def format_price(price: Any) -> str:
        try:
            return f"${float(price):.2f}" if price else "$0.00"
        except (ValueError, TypeError):
            return "$0.00"
    
    def format_volume(volume: Any) -> str:
        try:
            return f"{float(volume):,.0f}" if volume else "0"
        except (ValueError, TypeError):
            return "0"
    
    def get_color_for_change(change: Any) -> str:
        try:
            return "green" if float(change) > 0 else "red" if float(change) < 0 else "gray"
        except (ValueError, TypeError):
            return "gray"


def render_sidebar(symbols_df: pd.DataFrame) -> Tuple[str, Dict[str, Any]]:
    """
    Render sidebar with search, coin selection, and alert controls.

    Args:
        symbols_df: DataFrame with symbol data

    Returns:
        Tuple of (selected_symbol, alert_config)
    """
    st.sidebar.header("🚀 Crypto Dashboard")

    # Search and filter
    search_term = st.sidebar.text_input("🔍 Search Symbol", placeholder="BTC, ETH, ADA...")

    # Filter symbols based on search
    if search_term:
        filtered_symbols = symbols_df[
            symbols_df["symbol"].str.contains(search_term.upper(), na=False)
        ]
    else:
        filtered_symbols = symbols_df

    # Symbol selection
    if not filtered_symbols.empty:
        symbol_options = filtered_symbols["symbol"].tolist()
        selected_symbol = str(
            st.sidebar.selectbox("📈 Select Cryptocurrency", options=symbol_options, index=0)
        )
    else:
        st.sidebar.warning("No symbols found matching search term")
        selected_symbol = "BTCUSDT"

    st.sidebar.markdown("---")

    # Alert configuration
    st.sidebar.header("🔔 Price Alerts")

    alert_type = st.sidebar.radio(
        "Alert Type", options=["Price Target", "Percentage Change"], key="alert_type"
    )

    alert_config: Dict[str, Any] = {"enabled": False}

    if alert_type == "Price Target":
        price_target = st.sidebar.number_input(
            "Target Price ($)", min_value=0.0, value=0.0, step=0.01, format="%.8f"
        )

        direction = st.sidebar.radio(
            "Alert Direction", options=["Above", "Below"], key="price_direction"
        )

        if price_target > 0:
            alert_config: Dict[str, Any] = {
                "enabled": True,
                "type": "price",
                "target": price_target,
                "direction": direction.lower(),
            }

    else:  # Percentage Change
        percentage_change = st.sidebar.number_input(
            "Percentage Change (%)", min_value=-100.0, max_value=100.0, value=0.0, step=0.1
        )

        time_window = st.sidebar.selectbox(
            "Time Window",
            options=[60, 300, 900, 1800, 3600],
            format_func=lambda x: f"{x//60} minutes" if x < 3600 else f"{x//3600} hour(s)",
            index=1,
        )

        if percentage_change != 0:
            alert_config: Dict[str, Any] = {
                "enabled": True,
                "type": "percentage",
                "target": percentage_change,
                "window": time_window,
            }

    # Display settings
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Display Settings")

    chart_points = st.sidebar.slider(
        "Chart Points", min_value=50, max_value=500, value=150, step=50
    )

    refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", min_value=1, max_value=10, value=2)

    alert_config.update({"chart_points": chart_points, "refresh_rate": refresh_rate})

    return selected_symbol, alert_config


def render_top_symbols_table(df: pd.DataFrame) -> None:
    """
    Render enhanced table showing top cryptocurrency symbols with comprehensive data.

    Args:
        df: DataFrame with symbol data including enhanced metrics
    """
    if df.empty:
        st.error("No data available")
        return

    st.header("📊 Top Cryptocurrencies")

    # Enhanced sort options
    col1, col2, col3 = st.columns(3)
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            options=["volume", "priceChangePercent", "price", "marketCapProxy", "volatility", "trades"],
            format_func=lambda x: {
                "volume": "Volume (24h)",
                "priceChangePercent": "24h Change %", 
                "price": "Current Price",
                "marketCapProxy": "Market Activity",
                "volatility": "Volatility",
                "trades": "Trade Count"
            }.get(x, str(x)),  # type: ignore
            index=0
        )

    with col2:
        sort_order = st.selectbox(
            "Order",
            options=["desc", "asc"],
            format_func=lambda x: "Descending" if x == "desc" else "Ascending",
        )
    
    with col3:
        show_count = st.selectbox("Show", options=[10, 20, 50, 100], index=1)

    # Sort dataframe
    df_sorted = df.sort_values(sort_by, ascending=(sort_order == "asc"))  # type: ignore

    # Enhanced display with more comprehensive data
    st.markdown("### 📈 Live Market Data")
    
    for idx, (_, row) in enumerate(df_sorted.head(show_count).iterrows()):
        with st.container():
            # Main row with key metrics
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1.5, 1.5, 1, 1])

            with col1:
                # Symbol with rank
                rank = row.get('rank', idx + 1)
                st.markdown(f"**#{rank} {clean_symbol_name(row['symbol'])}**")
                st.caption(row["symbol"])

            with col2:
                # Price with precision
                price = row["price"]
                if price < 0.01:
                    price_str = f"${price:.8f}"
                elif price < 1:
                    price_str = f"${price:.6f}"
                else:
                    price_str = f"${price:.4f}"
                st.write(price_str)

            with col3:
                # 24h Change with color
                change = row["priceChangePercent"]
                color = get_color_for_change(change)
                st.markdown(
                    f"<span style='color: {color}; font-weight: bold'>{format_percentage(change)}</span>",
                    unsafe_allow_html=True,
                )

            with col4:
                # Volume
                st.write(format_volume(row["volume"]))

            with col5:
                # Trade count
                trades = row.get("trades", 0)
                if trades > 1000000:
                    st.write(f"{trades/1000000:.1f}M")
                elif trades > 1000:
                    st.write(f"{trades/1000:.1f}K")
                else:
                    st.write(f"{trades:,}")

            with col6:
                # 24h High/Low if available
                if 'high24h' in row and 'low24h' in row:
                    high = row['high24h']
                    low = row['low24h']
                    try:
                        if high is not None and low is not None and not pd.isna(high) and not pd.isna(low):  # type: ignore
                            range_pct = ((high - low) / low * 100) if low > 0 else 0
                            st.write(f"±{range_pct:.1f}%")
                            st.caption("24h Range")
                        else:
                            st.write("—")
                    except:
                        st.write("—")
                else:
                    st.write("—")

            # Additional metrics row (expandable)
            if st.checkbox(f"Details for {clean_symbol_name(row['symbol'])}", key=f"details_{row['symbol']}"):
                detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
                
                with detail_col1:
                    if 'high24h' in row and row['high24h'] is not None:
                        try:
                            if not pd.isna(row['high24h']):  # type: ignore
                                st.metric("24h High", f"${row['high24h']:.8f}" if row['high24h'] < 0.01 else f"${row['high24h']:.4f}")
                        except:
                            pass
                
                with detail_col2:
                    if 'low24h' in row and row['low24h'] is not None:
                        try:
                            if not pd.isna(row['low24h']):  # type: ignore
                                st.metric("24h Low", f"${row['low24h']:.8f}" if row['low24h'] < 0.01 else f"${row['low24h']:.4f}")
                        except:
                            pass
                
                with detail_col3:
                    if 'volatility' in row and row['volatility'] is not None:
                        try:
                            if not pd.isna(row['volatility']):  # type: ignore
                                st.metric("Volatility", f"{row['volatility']:.2f}%")
                        except:
                            pass
                
                with detail_col4:
                    if 'quoteVolume' in row and row['quoteVolume'] is not None:
                        try:
                            if not pd.isna(row['quoteVolume']):  # type: ignore
                                quote_vol = row['quoteVolume']
                                if quote_vol > 1000000:
                                    st.metric("Quote Volume", f"${quote_vol/1000000:.1f}M")
                                else:
                                    st.metric("Quote Volume", f"${quote_vol:,.0f}")
                        except:
                            pass

        st.divider()

    # Summary statistics
    st.markdown("### 📊 Market Summary")
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        gainers = len(df_sorted[df_sorted['priceChangePercent'] > 0])
        st.metric("🟢 Gainers", f"{gainers}/{len(df_sorted)}")
    
    with summary_col2:
        losers = len(df_sorted[df_sorted['priceChangePercent'] < 0])
        st.metric("🔴 Losers", f"{losers}/{len(df_sorted)}")
    
    with summary_col3:
        avg_change = df_sorted['priceChangePercent'].mean()
        st.metric("📈 Avg Change", f"{avg_change:.2f}%")
    
    with summary_col4:
        total_volume = df_sorted['volume'].sum()
        st.metric("💰 Total Volume", format_volume(total_volume))


def render_price_chart(timestamps: List[float], prices: List[float], symbol: str) -> None:
    """
    Render live price chart with sparkline.

    Args:
        timestamps: List of timestamps
        prices: List of price values
        symbol: Trading symbol
    """
    if not timestamps or not prices:
        st.info("Waiting for live data...")
        return

    # Convert timestamps to datetime for better display
    from datetime import datetime

    datetimes = [datetime.fromtimestamp(ts) for ts in timestamps]

    # Create plotly chart
    fig = go.Figure()

    # Add price line
    fig.add_trace(  # type: ignore
        go.Scatter(
            x=datetimes,
            y=prices,
            mode="lines",
            name="Price",
            line=dict(color="#1f77b4", width=2),
            hovertemplate="<b>%{y}</b><br>%{x}<extra></extra>",
        )
    )

    # Update layout
    fig.update_layout(  # type: ignore
        title=f"{clean_symbol_name(symbol)} Live Price",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        height=400,
        showlegend=False,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    # Style axes
    fig.update_xaxes(gridcolor="rgba(128,128,128,0.2)", tickformat="%H:%M:%S")  # type: ignore
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.2)", tickformat="$.8f")  # type: ignore

    st.plotly_chart(fig, use_container_width=True)  # type: ignore


def render_metrics(
    current_price: Optional[float], price_change: Optional[float], symbol: str
) -> None:
    """
    Render key metrics for selected cryptocurrency.

    Args:
        current_price: Current price value
        price_change: Price change percentage
        symbol: Trading symbol
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        if current_price is not None:
            st.metric(label="💰 Current Price", value=format_price(current_price))
        else:
            st.metric(label="💰 Current Price", value="Loading...")

    with col2:
        if price_change is not None:
            st.metric(
                label="📈 1-Min Change",
                value=format_percentage(price_change),
                delta=format_percentage(price_change),
            )
        else:
            st.metric(label="📈 1-Min Change", value="Loading...")

    with col3:
        st.metric(label="🔄 Symbol", value=clean_symbol_name(symbol))


def check_and_display_alerts(
    current_price: Optional[float],
    price_change: Optional[float],
    alert_config: Dict[str, Any],
    symbol: str,
) -> None:
    """
    Check alert conditions and display notifications.

    Args:
        current_price: Current price
        price_change: Recent price change percentage
        alert_config: Alert configuration
        symbol: Trading symbol
    """
    if not alert_config.get("enabled") or current_price is None:
        return

    alert_triggered = False
    alert_message = ""

    if alert_config["type"] == "price":
        target = alert_config["target"]
        direction = alert_config["direction"]

        if direction == "above" and current_price >= target:
            alert_triggered = True
            alert_message = (
                f"🔔 {clean_symbol_name(symbol)} reached ${target:,.8f}! "
                f"Current: {format_price(current_price)}"
            )
        elif direction == "below" and current_price <= target:
            alert_triggered = True
            alert_message = (
                f"🔔 {clean_symbol_name(symbol)} dropped to ${target:,.8f}! "
                f"Current: {format_price(current_price)}"
            )

    elif alert_config["type"] == "percentage" and price_change is not None:
        target = alert_config["target"]

        if (target > 0 and price_change >= target) or (target < 0 and price_change <= target):
            alert_triggered = True
            alert_message = (
                f"🔔 {clean_symbol_name(symbol)} moved "
                f"{format_percentage(price_change)} in the last minute!"
            )

    if alert_triggered:
        st.toast(alert_message, icon="🔔")
        st.success(alert_message)


def render_connection_status(is_connected: bool, symbol: str) -> None:
    """
    Render connection status indicator.

    Args:
        is_connected: Whether WebSocket is connected
        symbol: Current symbol
    """
    status_color = "🟢" if is_connected else "🔴"
    status_text = "Connected" if is_connected else "Disconnected"

    st.caption(f"{status_color} WebSocket: {status_text} ({symbol})")


def render_data_info(data_points: int, last_update: Optional[float]) -> None:
    """
    Render data information panel.

    Args:
        data_points: Number of data points
        last_update: Timestamp of last update
    """
    col1, col2 = st.columns(2)

    with col1:
        st.caption(f"📊 Data Points: {data_points}")

    with col2:
        if last_update:
            try:
                from utils import time_ago
            except ImportError:
                def time_ago(timestamp: float) -> str:
                    import time
                    now = time.time()
                    diff = now - timestamp
                    if diff < 60:
                        return f"{int(diff)}s ago"
                    elif diff < 3600:
                        return f"{int(diff/60)}m ago"
                    else:
                        return f"{int(diff/3600)}h ago"

            st.caption(f"🕐 Last Update: {time_ago(last_update)}")
        else:
            st.caption("🕐 Last Update: Never")
