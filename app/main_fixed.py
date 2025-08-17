"""Main Streamlit application for crypto real-time dashboard."""

import logging
import sys
import time
from pathlib import Path

# Add the parent directory to Python path to enable absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_streamlit_running():
    """Check if we're running in a Streamlit environment."""
    try:
        # Check if we're being run via streamlit by looking for streamlit in sys.modules
        # and checking if we have access to streamlit context
        import sys
        if 'streamlit' not in sys.modules:
            return False
        import streamlit as st
        # This will raise an exception if not in Streamlit context
        _ = st.session_state
        return True
    except Exception:
        return False

def main():
    """Main function that loads modules and runs the dashboard only in Streamlit context."""
    if not is_streamlit_running():
        print("⚠️  This application is designed to run with Streamlit.")
        print("Please use: streamlit run app/main.py")
        return
    
    import streamlit as st
    
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
        from .enhanced_features import (
            create_portfolio_tracker, create_technical_indicators, create_market_heatmap,
            create_alert_history, create_price_comparison, create_news_feed, create_export_features
        )
        from .theme_config import apply_custom_css, create_theme_toggle
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
        from app.enhanced_features import (
            create_portfolio_tracker, create_technical_indicators, create_market_heatmap,
            create_alert_history, create_price_comparison, create_news_feed, create_export_features
        )
        from app.theme_config import apply_custom_css, create_theme_toggle

    # Initialize Streamlit configuration and custom styling
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
    
    # Apply custom CSS
    apply_custom_css()
    
    # Create theme toggle
    create_theme_toggle()

    # Initialize session state
    if "selected_symbols" not in st.session_state:
        st.session_state.selected_symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
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

    # Main dashboard layout
    st.title("📈 Crypto Real-Time Dashboard")
    
    # Sidebar for controls and information
    with st.sidebar:
        st.header("Dashboard Controls")
        
        # Data source selection
        data_source = st.selectbox(
            "Select Data Source",
            options=["binance", "coinbase", "kraken"],
            index=0,
            key="data_source_selector",
            on_change=lambda: setattr(st.session_state, 'data_source', st.session_state.data_source_selector)
        )
        
        # Symbol selection
        available_symbols = get_top_symbols(st.session_state.data_source)
        selected_symbols = st.multiselect(
            "Select Trading Pairs",
            options=available_symbols,
            default=st.session_state.selected_symbols[:3],  # Limit to 3 for performance
            key="symbol_selector"
        )
        
        if selected_symbols != st.session_state.selected_symbols:
            st.session_state.selected_symbols = selected_symbols[:3]  # Limit to 3
            st.rerun()
        
        render_sidebar()

    # Connection status and data info
    col1, col2 = st.columns([1, 1])
    with col1:
        render_connection_status()
    with col2:
        render_data_info()

    # Main content area
    if st.session_state.selected_symbols:
        # Initialize or get existing WebSocket connection
        if "price_stream" not in st.session_state or not st.session_state.get("price_stream"):
            st.session_state.price_stream = PriceStream(
                exchange=st.session_state.data_source,
                symbols=st.session_state.selected_symbols
            )

        # Get real-time data
        price_stream = st.session_state.price_stream
        
        # Update symbols if changed
        if set(price_stream.symbols) != set(st.session_state.selected_symbols):
            price_stream.update_symbols(st.session_state.selected_symbols)

        # Get current data
        current_data = price_stream.get_current_data()
        historical_data = price_stream.get_historical_data()
        
        if current_data:
            st.session_state.websocket_data = current_data
            st.session_state.connection_status = "Connected"
        else:
            st.session_state.connection_status = "Connecting..."

        # Render metrics
        render_metrics(current_data)

        # Enhanced features tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Price Charts", 
            "💼 Portfolio", 
            "📈 Technical Analysis", 
            "🔥 Market Heatmap", 
            "🚨 Alerts", 
            "📰 News", 
            "💾 Export"
        ])
        
        with tab1:
            if historical_data:
                render_price_chart(historical_data, st.session_state.selected_symbols[0])
                render_top_symbols_table(current_data)
            else:
                st.info("Loading price data...")
                
        with tab2:
            create_portfolio_tracker()
            
        with tab3:
            if historical_data:
                create_technical_indicators(historical_data)
            else:
                st.info("Loading technical analysis data...")
                
        with tab4:
            if current_data:
                create_market_heatmap(current_data)
            else:
                st.info("Loading market data...")
                
        with tab5:
            create_alert_history()
            if current_data:
                check_and_display_alerts(current_data)
                
        with tab6:
            create_news_feed()
            
        with tab7:
            if current_data or historical_data:
                create_export_features(current_data, historical_data)
            else:
                st.info("No data available for export")

        # Price comparison section
        st.subheader("💱 Price Comparison")
        create_price_comparison(current_data)

    else:
        st.warning("Please select at least one trading pair from the sidebar to start monitoring.")
        st.info("💡 **Tip**: You can select up to 3 trading pairs for optimal performance.")

    # Auto-refresh mechanism with user control
    refresh_rate = st.sidebar.slider("Auto-refresh interval (seconds)", 1, 30, 5)
    
    # Add refresh status
    current_time = time.time()
    if current_time - st.session_state.last_refresh >= refresh_rate:
        st.session_state.last_refresh = current_time
        # Only rerun if we have new data or user interactions
        if st.session_state.websocket_data:
            st.rerun()
    else:
        # Add a progress bar to show refresh countdown
        progress = (current_time - st.session_state.last_refresh) / refresh_rate
        st.progress(progress, text=f"Next update in {refresh_rate - int(current_time - st.session_state.last_refresh)}s")

if __name__ == "__main__":
    # Check if we're running directly (not via streamlit)
    import sys
    if not any('streamlit' in arg for arg in sys.argv):
        # We're running directly, so launch with Streamlit automatically
        import subprocess
        import os
        
        print("🚀 Starting Crypto Real-Time Dashboard...")
        print("Launching with Streamlit for optimal experience...")
        
        # Get the current script path
        script_path = os.path.abspath(__file__)
        
        try:
            # Launch streamlit run with this script
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", script_path,
                "--server.port", "8501",
                "--server.address", "localhost",
                "--browser.gatherUsageStats", "false"
            ], check=True)
        except subprocess.CalledProcessError as e:
            # Check if it's a port conflict
            error_output = str(e)
            if "Port 8501 is already in use" in error_output or "already in use" in error_output:
                print("✅ Dashboard is already running!")
                print("🌐 Open your browser to: http://localhost:8501")
            else:
                print(f"❌ Failed to launch Streamlit: {e}")
                print("\n📋 Manual launch options:")
                print(f"  streamlit run {script_path}")
                print("  or")
                print("  pip install streamlit  (if not installed)")
        except FileNotFoundError:
            print("❌ Streamlit not found. Please install it first:")
            print("  pip install streamlit")
            print(f"\nThen run: streamlit run {script_path}")
    else:
        # We're being run via streamlit, so start the app
        main()
