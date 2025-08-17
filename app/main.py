"""Main Streamlit application for crypto real-time dashboard."""
import sys
import os
import time
import logging
import atexit
import subprocess
from pathlib import Path
from typing import Dict, Any, List, cast
import pandas as pd  # type: ignore
import streamlit as st

# from models import SessionStateManager  # Unused in fallback mode
# from websocket_manager import get_websocket_manager  # Unused in fallback mode

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Try imports with fallback
try:
    from data_sources import get_top_symbols
    from ui_components import (  # type: ignore
        render_connection_status,
        render_data_info,
        render_price_chart,
    )
    from ws_client import PriceStream  # type: ignore
    from theme_config import apply_custom_css, create_theme_toggle
    from enhanced_features import (  # type: ignore
        create_market_heatmap,
        create_portfolio_tracker,
        create_technical_indicators,
        create_alert_history,
        create_news_feed,
        create_export_features,
    )
except ImportError as e:
    logger.error(f"Import error: {e}")
    # Create minimal fallback functions to prevent crashes
    def get_top_symbols(limit: int = 50) -> pd.DataFrame:
        """Fallback function for get_top_symbols"""
        import pandas as pd
        # Return a minimal DataFrame with popular crypto symbols
        popular_symbols = [
            {"symbol": "BTCUSDT", "price": "50000", "pricechangepercent": "2.5"},
            {"symbol": "ETHUSDT", "price": "3000", "pricechangepercent": "1.8"},
            {"symbol": "BNBUSDT", "price": "400", "pricechangepercent": "-0.5"},
            {"symbol": "ADAUSDT", "price": "0.5", "pricechangepercent": "3.2"},
            {"symbol": "SOLUSDT", "price": "100", "pricechangepercent": "5.1"},
        ]
        return pd.DataFrame(popular_symbols)
    
    def render_connection_status(is_connected: bool, symbol: str) -> None:
        """Fallback function for render_connection_status"""
        status = "🟢 Connected" if is_connected else "🔴 Disconnected"
        st.metric("Connection", status)
        st.metric("Symbol", symbol)
    
    def render_data_info(data_points: int, last_refresh: float) -> None:
        """Fallback function for render_data_info"""
        st.metric("Data Points", data_points)
        st.metric("Last Update", time.strftime("%H:%M:%S", time.localtime(last_refresh)))
    
    def render_price_chart(timestamps: List[float], prices: List[float], symbol: str) -> None:
        """Fallback function for render_price_chart"""
        if timestamps and prices:
            import plotly.graph_objects as go  # type: ignore
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=timestamps, y=prices, mode='lines', name=symbol))  # type: ignore
            fig.update_layout(title=f"{symbol} Price Chart", xaxis_title="Time", yaxis_title="Price")  # type: ignore
            st.plotly_chart(fig, use_container_width=True)  # type: ignore
        else:
            st.info("No chart data available")
    
    def apply_custom_css() -> None:
        """Fallback function for apply_custom_css"""
        st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def create_theme_toggle() -> None:
        """Fallback function for create_theme_toggle"""
        pass
    
    # Create placeholder functions for enhanced features
    def create_market_heatmap(df: pd.DataFrame) -> None:
        st.subheader("📊 Market Heatmap")
        st.info("Market heatmap feature loading...")
    
    def create_portfolio_tracker() -> None:
        st.subheader("💼 Portfolio Tracker")
        st.info("Portfolio tracker feature loading...")
    
    def create_technical_indicators(prices: List[float], timestamps: List[float]) -> None:
        st.subheader("📈 Technical Indicators")
        st.info("Technical indicators feature loading...")
    
    def create_alert_history() -> None:
        st.subheader("🔔 Alert History")
        st.info("Alert history feature loading...")
    
    def create_news_feed() -> None:
        st.subheader("📰 News Feed")
        st.info("News feed feature loading...")
    
    def create_export_features() -> None:
        st.subheader("📥 Export Features")
        st.info("Export features loading...")
    
    # Create PriceStream fallback
    class PriceStream:
        def __init__(self) -> None:
            self.running = False
            self.symbol = None
        
        def start(self, symbol: str) -> None:
            self.symbol = symbol
            self.running = True
        
        def stop(self) -> None:
            self.running = False
        
        def get_series(self) -> tuple[List[float], List[float]]:
            return [], []
    
    st.warning("⚠️ Running in fallback mode. Some features may be limited.")
    logger.warning("Running with fallback functions due to import errors")
from typing import Dict, Any, List, cast
import pandas as pd  # type: ignore
import streamlit as st

# from models import SessionStateManager  # Already imported above
# from websocket_manager import get_websocket_manager  # Already imported above

# Add the parent directory to Python path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import modules with error handling
try:
    # Try relative imports first (when run via streamlit)
    from data_sources import get_top_symbols
    from ui_components import (
        render_connection_status,
        render_data_info,
        render_price_chart,
    )
    from ws_client import PriceStream
    from theme_config import apply_custom_css, create_theme_toggle
    from enhanced_features import (
        create_market_heatmap,
        create_portfolio_tracker,
        create_technical_indicators,
        create_alert_history,
        create_news_feed,
        create_export_features,
    )
except ImportError as e:
    logger.info(f"Some optional modules not found: {e}")
    # Fallback functions already defined above
    # Note: This is normal if some enhanced features are not available

def cleanup_streams() -> None:
    """Cleanup function to stop all streams on application shutdown."""
    try:
        if hasattr(st.session_state, 'price_stream') and st.session_state.price_stream:
            st.session_state.price_stream.stop()
            logger.info("Cleaned up WebSocket streams on shutdown")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Register cleanup function
atexit.register(cleanup_streams)

def add_log_message(message: str, level: str = "INFO") -> None:
    """Add a log message to both console and session state."""
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {level}: {message}"
    
    # Log to console
    if level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)
    
    # Store in session state for display
    if "log_messages" not in st.session_state:
        st.session_state.log_messages = []
    
    # Get current log messages and append new one
    current_logs: List[str] = getattr(st.session_state, "log_messages", [])
    current_logs.append(formatted_msg)
    
    # Keep only last 100 messages to prevent memory issues
    if len(current_logs) > 100:
        current_logs = current_logs[-100:]
    
    st.session_state.log_messages = current_logs

def setup_session_state() -> None:
    """Initialize session state variables."""
    if "selected_symbols" not in st.session_state:
        st.session_state.selected_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    if "websocket_data" not in st.session_state:
        st.session_state.websocket_data = {}
    if "alerts" not in st.session_state:
        st.session_state.alerts = []
    if "connection_status" not in st.session_state:
        st.session_state.connection_status = "Disconnected"
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()
    if "data_source" not in st.session_state:
        st.session_state.data_source = "binance"
    if "price_stream" not in st.session_state:
        st.session_state.price_stream = None
    if "current_symbol" not in st.session_state:
        st.session_state.current_symbol = None
    # auto_refresh and refresh_rate will be handled by the widgets directly
    # No manual session state initialization needed for widget-controlled values

def get_session_state_value(key: str, default: Any = None) -> Any:
    """Helper to get session state values with type safety."""
    return getattr(st.session_state, key, default)

def render_sidebar_section(symbols_df: pd.DataFrame) -> List[str]:
    """Render the sidebar with controls."""
    with st.sidebar:
        st.header("🔧 Dashboard Controls")
        
        # Data source selector
        st.selectbox(
            "Data Source",
            options=["binance", "coinbase", "kraken"],
            index=0,
            key="data_source",
            help="Select cryptocurrency data source"
        )
        
        # Symbol selector
        available_symbols = symbols_df['symbol'].tolist() if not symbols_df.empty else []
        
        # Graceful first-run: handle empty symbols
        if not available_symbols:
            st.warning("⚠️ No symbols available. This might be due to an API issue.")
            if st.button("🔄 Retry Loading Symbols"):
                # Clear cache and retry
                if 'load_market_data' in st.session_state:
                    st.cache_data.clear()
                st.rerun()
            return []
        
        # Ensure default symbols exist in available options
        default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT", "MATICUSDT", "AVAXUSDT"]
        valid_defaults = [symbol for symbol in default_symbols if symbol in available_symbols]
        if not valid_defaults and available_symbols:
            valid_defaults = available_symbols[:5]  # Take first 5 if defaults don't exist
        
        # Add coin search/filter
        st.markdown("**🔍 Search Coins:**")
        search_term = st.text_input("Type to filter coins (e.g., BTC, ETH, ADA):", placeholder="Enter coin symbol...", key="coin_search")
        
        # Filter available symbols based on search
        if search_term:
            filtered_symbols = [symbol for symbol in available_symbols if search_term.upper() in symbol.upper()]
            if filtered_symbols:
                available_symbols = filtered_symbols
            else:
                st.warning(f"No coins found matching '{search_term}'. Showing all coins.")
        
        # Display popular coins for quick selection
        st.markdown("**⭐ Popular Coins:**")
        popular_coins = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT", "MATICUSDT", "AVAXUSDT"]
        popular_available = [coin for coin in popular_coins if coin in available_symbols]
        
        if popular_available:
            cols = st.columns(4)
            for i, coin in enumerate(popular_available[:8]):  # Show top 8 popular coins
                col = cols[i % 4]
                with col:
                    if st.button(f"➕ {coin.replace('USDT', '')}", key=f"add_{coin}", help=f"Add {coin} to selection"):
                        current_selection = st.session_state.get("selected_symbols", [])
                        if coin not in current_selection and len(current_selection) < 10:
                            current_selection.append(coin)
                            st.session_state.selected_symbols = current_selection
                            st.rerun()
        
        selected_symbols = st.multiselect(
            "📊 Select Trading Pairs",
            options=available_symbols,
            default=valid_defaults,
            max_selections=10,  # Increased from 5 to 10
            help="Select up to 10 trading pairs to monitor. Popular pairs: BTC, ETH, BNB, ADA, SOL, DOT, MATIC, AVAX"
        )
        
        # Update session state
        if selected_symbols:
            st.session_state.selected_symbols = selected_symbols
        
        # Refresh controls with real-time settings
        st.subheader("⚡ Real-Time Settings")
        auto_refresh = st.checkbox("🔄 Auto-refresh enabled", value=True, key="auto_refresh")
        if auto_refresh:
            refresh_rate = st.slider("Auto-refresh (seconds)", 1, 10, 2, key="refresh_rate", 
                                   help="Lower values = more real-time updates")
            st.info(f"📡 Auto-refreshing every {refresh_rate} seconds")
        else:
            st.warning("⏸️ Auto-refresh is disabled")
        
        # Chart settings
        st.subheader("📊 Chart Settings")
        st.selectbox(
            "Chart Time Window",
            options=["1h", "4h", "24h"],
            index=2,  # Default to 24h
            key="chart_window",
            help="Select the time window for price charts"
        )
        
        if st.button("🔄 Manual Refresh"):
            st.session_state.last_refresh = 0  # Force refresh
            st.rerun()
        
        # Debug/Logging area
        st.subheader("🔍 Debug Logs")
        with st.expander("View Logs", expanded=False):
            # Get recent logs from session state
            log_messages = get_session_state_value("log_messages", [])
            if log_messages:
                for log_msg in log_messages[-20:]:  # Show last 20 log messages for better display
                    st.text(log_msg)
            else:
                st.text("No logs available")
            
            if st.button("Clear Logs"):
                st.session_state.log_messages = []
                st.rerun()
        
        return selected_symbols

def render_connection_info() -> None:
    """Render connection status and data info."""
    # WebSocket health check
    websocket_data = get_session_state_value("websocket_data", {})
    current_symbol = get_session_state_value("current_symbol")
    
    if current_symbol and current_symbol in websocket_data:
        last_timestamp = websocket_data[current_symbol].get('timestamp', 0)
        if time.time() - last_timestamp > 10:  # No data for 10 seconds
            st.session_state.connection_status = "Reconnecting..."
            add_log_message(f"WebSocket health check failed for {current_symbol} - setting to reconnecting", "WARNING")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        is_connected = get_session_state_value("connection_status") == "Connected"
        current_symbol = get_session_state_value("current_symbol", "No Symbol")
        render_connection_status(is_connected, current_symbol)
    
    with col2:
        websocket_data = cast(Dict[str, Any], get_session_state_value("websocket_data", {}))
        data_points = len(websocket_data)
        last_refresh = get_session_state_value("last_refresh", time.time())
        render_data_info(data_points, last_refresh)

def manage_websocket_connection(selected_symbols: List[str]) -> None:
    """Manage WebSocket connection for selected symbols."""
    if not selected_symbols:
        # Stop existing stream when no symbols are selected
        existing_stream = get_session_state_value("price_stream")
        if existing_stream:
            existing_stream.stop()
            st.session_state.price_stream = None
            st.session_state.connection_status = "Disconnected"
            st.session_state.current_symbol = None
            add_log_message("Stopped WebSocket connection - no symbols selected", "INFO")
        return
    
    current_symbol = selected_symbols[0]  # Use first selected symbol
    
    # Check if we need to start/restart WebSocket (only if symbol changed or no stream exists)
    existing_stream = get_session_state_value("price_stream")
    current_stored_symbol = get_session_state_value("current_symbol")
    
    need_new_connection = (
        current_stored_symbol != current_symbol or 
        existing_stream is None or
        (hasattr(existing_stream, 'running') and not existing_stream.running)
    )
    
    if need_new_connection:
        try:
            # Stop existing stream if it exists
            if existing_stream:
                existing_stream.stop()
                add_log_message("Stopped existing WebSocket connection", "INFO")
            
            # Start new stream with lowercase symbol (Binance requirement)
            start_symbol = current_symbol.lower()  # binance streams are lowercase
            st.session_state.price_stream = PriceStream()  # Initialize without symbol
            st.session_state.price_stream.start(start_symbol)  # Pass symbol to start method
            st.session_state.current_symbol = current_symbol
            st.session_state.connection_status = "Connected"
            
            add_log_message(f"Started WebSocket for {current_symbol} (stream: {start_symbol})", "INFO")
            
        except Exception as e:
            error_msg = f"WebSocket connection error: {e}"
            add_log_message(error_msg, "ERROR")
            logger.exception("WebSocket connection error")
            # Ensure state is properly set to disconnected on failure
            st.session_state.connection_status = "Disconnected"
            st.session_state.price_stream = None
            st.session_state.current_symbol = None
    else:
        # WebSocket is already running for the correct symbol
        add_log_message(f"WebSocket already running for {current_symbol}", "DEBUG")

def render_main_content(symbols_df: pd.DataFrame, selected_symbols: List[str]) -> None:
    """Render the main dashboard content."""
    if not selected_symbols:
        st.info("🔍 Please select at least one trading pair from the sidebar.")
        return
    
    # Get current symbol data
    symbol = selected_symbols[0]
    websocket_data = cast(Dict[str, Any], get_session_state_value("websocket_data", {}))
    
    # Get price stream data and update session state in real-time
    price_stream = get_session_state_value("price_stream")
    if price_stream:
        try:
            latest_price = price_stream.get_latest_price()
            add_log_message(f"Price stream status: price={latest_price}, data_count={len(price_stream.price_data) if hasattr(price_stream, 'price_data') else 'unknown'}", "DEBUG")
            
            if latest_price is not None:
                add_log_message(f"WebSocket latest price for {symbol}: ${latest_price:.6f}", "INFO")
                
                # Get historical data from symbols_df for price change calculation
                symbol_row = symbols_df[symbols_df['symbol'] == symbol]
                price_change_24h = 0.0
                
                if not symbol_row.empty:
                    # Try to get 24h change from the data source (columns are now normalized)
                    if 'pricechangepercent' in symbol_row.columns:
                        price_change_24h = float(symbol_row['pricechangepercent'].iloc[0])
                    elif 'price_change_percent' in symbol_row.columns:
                        price_change_24h = float(symbol_row['price_change_percent'].iloc[0])
                    elif 'change' in symbol_row.columns:
                        price_change_24h = float(symbol_row['change'].iloc[0])
                    else:
                        # Calculate change from previous price if available
                        previous_data = websocket_data.get(symbol, {})
                        previous_price = previous_data.get('price')
                        if previous_price and previous_price != latest_price:
                            price_change_24h = ((latest_price - previous_price) / previous_price) * 100
                        else:
                            price_change_24h = 0.0
                
                # Update websocket_data with latest price and calculated change
                if "websocket_data" not in st.session_state:
                    st.session_state.websocket_data = {}
                websocket_data = cast(Dict[str, Any], st.session_state.websocket_data)  # type: ignore
                websocket_data[symbol] = {
                    'price': latest_price,
                    'change': price_change_24h,
                    'timestamp': time.time()
                }
                
                # Refresh local reference
                websocket_data = cast(Dict[str, Any], st.session_state.websocket_data)  # type: ignore
                
                # Enhanced logging with tags
                source = get_session_state_value("data_source", "binance")
                add_log_message(f"[{source}|{symbol}] WebSocket Updated: ${latest_price:.6f} ({price_change_24h:+.2f}%)", "INFO")
            else:
                # Only log if WebSocket is connected but no data yet (normal during startup)
                if hasattr(price_stream, 'running') and price_stream.running:
                    add_log_message(f"WebSocket connected for {symbol}, waiting for first trade data...", "INFO")
                else:
                    add_log_message(f"WebSocket not running for {symbol}", "WARNING")
        except Exception as e:
            error_msg = f"Error getting stream data: {e}"
            add_log_message(error_msg, "ERROR")
            logger.exception("Error getting stream data")
    else:
        add_log_message(f"No price stream available for {symbol}", "WARNING")
    
    # Render metrics
    symbol_data = websocket_data.get(symbol, {})
    current_price = symbol_data.get('price')
    price_change = symbol_data.get('change', 0.0)
    
    # Get symbol data from symbols_df as fallback/primary source
    symbol_row = symbols_df[symbols_df['symbol'] == symbol]
    fallback_price = None
    fallback_change = 0.0
    
    if not symbol_row.empty:
        if 'price' in symbol_row.columns:
            fallback_price = float(symbol_row['price'].iloc[0])
        if 'pricechangepercent' in symbol_row.columns:
            fallback_change = float(symbol_row['pricechangepercent'].iloc[0])
    
    # Use WebSocket data if available, otherwise use symbols_df data
    display_price = current_price if current_price else fallback_price
    display_change = price_change if price_change != 0.0 else fallback_change
    
    # Log what we're displaying
    price_source = "WebSocket" if current_price else "API Data"
    change_source = "WebSocket" if price_change != 0.0 else "API Data"
    add_log_message(f"Displaying - Price: ${display_price} ({price_source}), Change: {display_change:.2f}% ({change_source})", "INFO")
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if display_price:
            # Adaptive decimals: more decimals for tiny prices
            price = float(display_price) if display_price is not None else None
            if price is not None:
                if price >= 100:    fmt = "${:.2f}"
                elif price >= 1:    fmt = "${:.4f}"  
                else:               fmt = "${:.8f}"
                st.metric("💰 Current Price", fmt.format(price))
            else:
                st.metric("💰 Current Price", "Loading...")
        else:
            st.metric("💰 Current Price", "Loading...")
    
    with col2:
        try:
            if display_change is not None and str(display_change).lower() not in ['nan', 'none', '']:
                change_value = float(display_change)
                st.metric("📈 24h Change", f"{change_value:.2f}%", delta=change_value)
            else:
                st.metric("📈 24h Change", "Loading...")
        except (ValueError, TypeError):
            st.metric("📈 24h Change", "Loading...")
    
    with col3:
        st.metric("📊 Symbol", symbol)
    
    with col4:
        status = get_session_state_value("connection_status", "Disconnected")
        color = "🟢" if status == "Connected" else "🔴"
        st.metric("🔗 Status", f"{color} {status}")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Market Overview", 
        "💼 Portfolio", 
        "📈 Technical Analysis", 
        "🔔 Alerts", 
        "📰 News & Export"
    ])
    
    with tab1:
        try:
            # Market heatmap
            create_market_heatmap(symbols_df)
            
            # Simple in-memory buffer as a fallback series
            if "chart_buffer" not in st.session_state:
                st.session_state.chart_buffer = {}

            chart_buffer = cast(Dict[str, Dict[str, List[float]]], st.session_state.chart_buffer)  # type: ignore
            buf = chart_buffer.setdefault(symbol, {"t": [], "p": []})
            if display_price is not None:
                buf["t"].append(time.time())
                buf["p"].append(float(display_price))
                buf["t"] = buf["t"][-600:]  # keep last 600 points
                buf["p"] = buf["p"][-600:]

            # Price chart with fallback logic
            if price_stream:
                timestamps, prices = price_stream.get_series()
                if not timestamps or not prices:
                    # Fall back to our buffer so the chart shows immediately
                    timestamps, prices = buf["t"], buf["p"]
                
                add_log_message(f"[{symbol}] series len: {len(timestamps)}", "DEBUG")
                
                if timestamps and prices:
                    render_price_chart(timestamps, prices, symbol)
                else:
                    st.info("📡 Waiting for real-time data...")
            else:
                st.info("🔌 Connecting to data stream...")
                
        except Exception as e:
            error_msg = f"Error in market overview: {e}"
            add_log_message(error_msg, "ERROR")
            logger.exception("Error in market overview")
            st.error(error_msg)
            st.error("💡 **Try:** Select a different symbol or refresh the page")
    
    with tab2:
        try:
            create_portfolio_tracker()
        except Exception as e:
            error_msg = f"Error in portfolio section: {e}"
            add_log_message(error_msg, "ERROR")
            logger.exception("Error in portfolio section")
            st.error(error_msg)
            st.error("💡 **Try:** Refresh the page or clear browser cache")
    
    with tab3:
        try:
            timestamps, prices = [], []
            if price_stream:
                timestamps, prices = price_stream.get_series()
            
            # Convert timestamps for better plotting (keep it simple for compatibility)
            processed_timestamps = cast(List[float], timestamps) if timestamps else []
            processed_prices = cast(List[float], prices) if prices else []
            create_technical_indicators(processed_prices, processed_timestamps)
        except Exception as e:
            error_msg = f"Error in technical analysis: {e}"
            add_log_message(error_msg, "ERROR")
            logger.exception("Error in technical analysis")
            st.error(error_msg)
            st.error("💡 **Try:** Refresh the page or select a different symbol")
    
    with tab4:
        try:
            create_alert_history()
        except Exception as e:
            error_msg = f"Error in alerts section: {e}"
            add_log_message(error_msg, "ERROR")
            logger.exception("Error in alerts section")
            st.error(error_msg)
            st.error("💡 **Try:** Clear your alert history or refresh the page")
    
    with tab5:
        try:
            create_news_feed()
            create_export_features()
        except Exception as e:
            error_msg = f"Error in news/export section: {e}"
            add_log_message(error_msg, "ERROR")
            logger.exception("Error in news/export section")
            st.error(error_msg)
            st.error("💡 **Try:** Check your internet connection or try again later")

def main() -> None:
    """Main application function."""
    try:
        # Page configuration
        st.set_page_config(
            page_title="Crypto Real-Time Dashboard",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/yourusername/crypto-dashboard',
                'Report a bug': 'https://github.com/yourusername/crypto-dashboard/issues',
                'About': "Crypto Real-Time Dashboard - Real-time cryptocurrency price tracking and portfolio management"
            }
        )
        
        # Apply styling and setup
        apply_custom_css()
        create_theme_toggle()
        setup_session_state()
        
        # Main title
        st.title("📈 Crypto Real-Time Dashboard")
        st.markdown("---")
        
        # Load market data with caching for performance
        @st.cache_data(ttl=300)  # Cache for 5 minutes to reduce API load
        def load_market_data(limit: int = 100, source: str = "binance") -> pd.DataFrame:
            """Load market data with caching - cache key includes source."""
            # Use the selected data source in cache key
            add_log_message(f"Loading market data from {source} (limit: {limit})", "INFO")
            # TODO: Pass source to get_top_symbols when multi-source support is added
            return get_top_symbols(limit=limit)
        
        # Get selected data source
        source = get_session_state_value("data_source", "binance")
        
        with st.spinner("📡 Loading market data..."):
            try:
                symbols_df = load_market_data(limit=100, source=source)  # Load 100 coins instead of 50
                if symbols_df.empty:
                    error_msg = "Failed to load market data. Please try again."
                    add_log_message(error_msg, "ERROR")
                    st.error(f"❌ {error_msg}")
                    
                    # Graceful first-run: show retry button
                    if st.button("🔄 Retry Loading Data"):
                        load_market_data.clear()  # Clear cache
                        st.rerun()
                    st.stop()
                else:
                    # Normalize column names for consistent access (strip spaces too)
                    symbols_df.columns = [c.lower().strip() for c in symbols_df.columns]
                    add_log_message(f"Successfully loaded {len(symbols_df)} symbols from {source}", "INFO")
            except Exception as e:
                error_msg = f"Error loading market data: {e}"
                add_log_message(error_msg, "ERROR")
                st.error(f"❌ {error_msg}")
                st.error("💡 **Try:** Refresh the page or check your internet connection")
                
                # Graceful error recovery
                if st.button("🔄 Clear Cache & Retry"):
                    load_market_data.clear()
                    st.rerun()
                st.stop()
        
        # Render sidebar
        selected_symbols = render_sidebar_section(symbols_df)
        
        # Manage WebSocket connection
        manage_websocket_connection(selected_symbols)
        
        # Render connection info
        render_connection_info()
        
        # Auto-refresh status display (after sidebar is rendered)
        if st.session_state.get("auto_refresh", True):
            refresh_rate = st.session_state.get("refresh_rate", 2)
            
            # Add real-time status indicator
            _, col2, col3 = st.columns([2, 1, 1])
            with col2:
                st.success(f"🔴 LIVE - Refreshing every {refresh_rate}s")
            with col3:
                current_time = time.strftime("%H:%M:%S")
                st.info(f"🕐 {current_time}")
        else:
            st.warning("⏸️ Auto-refresh is disabled")
        
        st.markdown("---")
        
        # Render main content
        render_main_content(symbols_df, selected_symbols)
        
        # Auto-refresh logic for real-time updates
        current_time = time.time()
        last_refresh = get_session_state_value("last_refresh", 0)
        refresh_rate = st.session_state.get("refresh_rate", 2)  # Use user's choice from sidebar
        auto_refresh = st.session_state.get("auto_refresh", True)  # Default to True
        
        if auto_refresh and current_time - last_refresh >= refresh_rate:
            st.session_state.last_refresh = current_time
            # Refresh for real-time price updates
            websocket_data = get_session_state_value("websocket_data", {})
            if websocket_data or get_session_state_value("connection_status") in ["Connected", "Connecting"]:
                add_log_message(f"Auto-refreshing dashboard (rate: {refresh_rate}s)", "DEBUG")
                time.sleep(0.1)  # Small delay to prevent too frequent updates
                st.rerun()
        
        # Use st.rerun() for refresh instead of JavaScript to preserve session state
        if auto_refresh and current_time - last_refresh >= refresh_rate:
            st.rerun()
        
    except Exception as e:
        error_msg = f"Application error: {e}"
        add_log_message(error_msg, "ERROR")
        logger.exception("Application error")
        st.error(f"❌ {error_msg}")

def check_streamlit_context() -> bool:
    """Check if running in Streamlit context."""
    try:
        # Check if we have a proper Streamlit script run context
        from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx  # type: ignore
        return get_script_run_ctx() is not None
    except ImportError:
        # Streamlit not available or not imported yet
        return (
            'streamlit' in sys.modules or
            'STREAMLIT_SERVER_PORT' in os.environ or
            any('streamlit' in arg.lower() for arg in sys.argv)
        )
    except Exception:
        # Other errors (like missing context)
        return False

if __name__ == "__main__":
    if check_streamlit_context():
        main()
    else:
        print("🚀 Starting Crypto Real-Time Dashboard...")
        print("Launching with Streamlit for optimal experience...")
        try:
            import subprocess
            script_path = os.path.abspath(__file__)
            result = subprocess.run([
                sys.executable, "-m", "streamlit", "run", script_path,
                "--server.port", "8501",
                "--server.address", "localhost"
            ], check=False)
            if result.returncode != 0:
                print("❌ Failed to launch Streamlit. Please run manually:")
                print(f"   streamlit run {script_path}")
        except FileNotFoundError:
            print("❌ Streamlit not found. Please install with: pip install streamlit")
            print(f"Then run with: streamlit run {os.path.abspath(__file__)}")
        except Exception as e:
            print(f"❌ Error launching Streamlit: {e}")
            print("Please run manually:")
            print(f"   streamlit run {os.path.abspath(__file__)}")
