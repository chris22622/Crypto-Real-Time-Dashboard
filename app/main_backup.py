"""Main Streamlit application for crypto real-time dashboard."""

import logging
import sys
import time
from pathlib import Path

# Add the parent directory to Python path to enable absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# C        except subprocess.CalledProcessError as e:
            # Check if it's a port conflict
            if "Port 8501 is already in use" in str(e) or "already in use" in str(e):
                print("✅ Dashboard is already running!")
                print("🌐 Open your browser to: http://localhost:8501")
            else:
                print(f"❌ Failed to launch Streamlit: {e}")
                print("\n📋 Manual launch options:")
                print(f"  streamlit run {script_path}")
                print("  or")
                print("  pip install streamlit  (if not installed)")re logging
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

    # Page configuration
    st.set_page_config(
        page_title="Crypto Real-Time Dashboard",
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

    # Apply custom theme and styling
    apply_custom_css()

    # Header
    st.title("🚀 Crypto Real-Time Dashboard")
    st.markdown("Live cryptocurrency prices with real-time alerts and analytics")

    # Load top symbols data
    with st.spinner("Loading market data..."):
        symbols_df = get_top_symbols(limit=100)

    if symbols_df.empty:
        st.error("Failed to load market data. Please check your internet connection.")
        st.stop()

    # Store market data in session state for enhanced features
    st.session_state.market_data = symbols_df

    # Render sidebar
    selected_symbol, alert_config = render_sidebar(symbols_df)
    
    # Add theme toggle to sidebar
    create_theme_toggle()

    # Check if symbol changed
    if selected_symbol != st.session_state.current_symbol:
        st.session_state.current_symbol = selected_symbol
        st.session_state.price_stream.start(selected_symbol)
        logger.info(f"Started streaming for {selected_symbol}")

    # Main layout
    left_col, right_col = st.columns([1, 1])

    with left_col:
        render_top_symbols_table(symbols_df)

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

    # Enhanced Features Section
    st.markdown("---")
    
    # Create tabs for enhanced features
    try:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Market Heatmap", "💼 Portfolio", "📈 Advanced Charts", 
            "🔔 Alerts", "📰 News & Export"
        ])
        
        with tab1:
            # Market heatmap
            try:
                if 'market_data' in st.session_state:
                    heatmap_fig = create_market_heatmap(st.session_state.market_data)
                    if heatmap_fig:
                        st.plotly_chart(heatmap_fig, use_container_width=True)  # type: ignore
                else:
                    st.info("Loading market data...")
            except Exception as e:
                st.error(f"Error creating market heatmap: {e}")
        
        with tab2:
            # Portfolio tracker
            try:
                create_portfolio_tracker()
            except Exception as e:
                st.error(f"Error loading portfolio: {e}")
        
        with tab3:
            # Advanced technical charts
            try:
                timestamps, prices = st.session_state.price_stream.get_series()
                if len(timestamps) > 20:
                    tech_fig = create_technical_indicators(prices, [t for t in timestamps])
                    if tech_fig:
                        st.plotly_chart(tech_fig, use_container_width=True)  # type: ignore
                else:
                    st.info("Need more data points for technical analysis (minimum 20)")
                
                # Price comparison
                create_price_comparison()
            except Exception as e:
                st.error(f"Error creating technical charts: {e}")
        
        with tab4:
            # Alert history
            try:
                create_alert_history()
            except Exception as e:
                st.error(f"Error loading alert history: {e}")
        
        with tab5:
            try:
                col1, col2 = st.columns(2)
                with col1:
                    create_news_feed()
                with col2:
                    create_export_features()
            except Exception as e:
                st.error(f"Error loading news and export features: {e}")
    
    except Exception as e:
        st.error(f"Error creating enhanced features: {e}")
        st.info("Running in basic mode...")

    # Auto-refresh control with better performance
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
            print(f"❌ Failed to launch Streamlit: {e}")
            print("\n� Manual launch options:")
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
