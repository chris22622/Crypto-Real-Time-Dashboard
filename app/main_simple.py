"""Simplified main file for testing."""

import logging
import sys
import time
from pathlib import Path

import streamlit as st

# Add the parent directory to Python path to enable absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Try relative imports first (when run via streamlit run)
    from .data_sources import get_top_symbols
    from .ui_components import (
        check_and_display_alerts,
        render_connection_status,
        render_data_info,
        render_metrics,
        render_price_chart,
        render_sidebar,
        render_top_symbols_table,
    )
    from .ws_client import PriceStream
except ImportError:
    # Fall back to absolute imports (when run directly)
    from app.data_sources import get_top_symbols
    from app.ui_components import (
        check_and_display_alerts,
        render_connection_status,
        render_data_info,
        render_metrics,
        render_price_chart,
        render_sidebar,
        render_top_symbols_table,
    )
    from app.ws_client import PriceStream

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Crypto Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "price_stream" not in st.session_state:
    st.session_state.price_stream = PriceStream()

if "current_symbol" not in st.session_state:
    st.session_state.current_symbol = None

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0


def main():
    """Main application function."""

    # Header
    st.title("🚀 Crypto Real-Time Dashboard")
    st.markdown("Live cryptocurrency prices with real-time alerts and analytics")

    # Load top symbols data
    with st.spinner("Loading market data..."):
        symbols_df = get_top_symbols(limit=100)

    if symbols_df.empty:
        st.error("Failed to load market data. Please check your internet connection.")
        st.stop()

    # Store market data in session state
    st.session_state.market_data = symbols_df

    # Render sidebar
    selected_symbol, alert_config = render_sidebar(symbols_df)

    # Check if symbol changed
    if selected_symbol != st.session_state.current_symbol:
        st.session_state.current_symbol = selected_symbol
        st.session_state.price_stream.start(selected_symbol)

    # Main layout
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.header("📊 Top Cryptocurrencies")
        render_top_symbols_table(symbols_df.head(20))

    with right_col:
        st.header(f"📈 {selected_symbol} Live Chart")

        # Get live data
        timestamps, prices = st.session_state.price_stream.get_series()
        current_price = st.session_state.price_stream.get_latest_price()
        price_change = st.session_state.price_stream.get_price_change(window_seconds=60)

        # Render metrics
        render_metrics(current_price, price_change, selected_symbol)

        # Render chart
        if timestamps and prices:
            # Limit data points based on user preference
            max_points = alert_config.get("chart_points", 150)
            if len(timestamps) > max_points:
                timestamps = timestamps[-max_points:]
                prices = prices[-max_points:]

        render_price_chart(timestamps, prices, selected_symbol)

        # Connection status and data info
        is_connected = (
            st.session_state.price_stream.running
            and st.session_state.price_stream.current_symbol == selected_symbol
        )

        render_connection_status(is_connected, selected_symbol)
        render_data_info(len(timestamps), timestamps[-1] if timestamps else None)

        # Check alerts
        check_and_display_alerts(current_price, price_change, alert_config, selected_symbol)

    # Auto-refresh control
    refresh_rate = alert_config.get("refresh_rate", 2)
    current_time = time.time()
    
    # Use a more efficient refresh mechanism
    if current_time - st.session_state.last_refresh >= refresh_rate:
        st.session_state.last_refresh = current_time
        # Only rerun if we have new data or user interactions
        if timestamps and len(timestamps) > st.session_state.get('last_data_length', 0):
            st.session_state.last_data_length = len(timestamps)
            time.sleep(refresh_rate)
            st.rerun()
    else:
        # Add a progress bar to show refresh countdown
        progress = (current_time - st.session_state.last_refresh) / refresh_rate
        st.progress(progress, text=f"Next update in {refresh_rate - int(current_time - st.session_state.last_refresh)}s")


if __name__ == "__main__":
    main()
