"""Theme and styling configuration for the dashboard."""

from typing import Dict, Any
import streamlit as st  # type: ignore


def apply_custom_css() -> None:
    """Apply custom CSS styling to the dashboard."""
    
    # Check if dark mode is enabled
    dark_mode = st.session_state.get('dark_mode', False)
    
    if dark_mode:
        # Dark theme CSS
        css = """
        <style>
        .main > div {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        .stMetric {
            background-color: #262730;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #00d4aa;
        }
        
        .stAlert {
            background-color: #1e1e1e;
            border-radius: 8px;
        }
        
        .stSelectbox > div > div {
            background-color: #262730;
        }
        
        .stNumberInput > div > div {
            background-color: #262730;
        }
        
        .stTab {
            background-color: #262730;
        }
        
        .crypto-card {
            background: linear-gradient(145deg, #1e1e1e, #2d2d2d);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            border: 1px solid #333;
        }
        
        .price-positive {
            color: #00ff88;
            font-weight: bold;
        }
        
        .price-negative {
            color: #ff4444;
            font-weight: bold;
        }
        
        .glow-effect {
            box-shadow: 0 0 20px rgba(0, 212, 170, 0.3);
        }
        </style>
        """
    else:
        # Light theme CSS
        css = """
        <style>
        .main > div {
            background-color: #ffffff;
            color: #262626;
        }
        
        .stMetric {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #007bff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .stAlert {
            border-radius: 8px;
        }
        
        .crypto-card {
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border: 1px solid #e9ecef;
        }
        
        .price-positive {
            color: #28a745;
            font-weight: bold;
        }
        
        .price-negative {
            color: #dc3545;
            font-weight: bold;
        }
        
        .glow-effect {
            box-shadow: 0 0 20px rgba(0, 123, 255, 0.2);
        }
        </style>
        """
    
    st.markdown(css, unsafe_allow_html=True)


def create_theme_toggle() -> None:
    """Create a theme toggle button in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Theme Settings")
    
    # Initialize theme state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # Theme toggle
    dark_mode = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    # Additional styling options
    st.sidebar.subheader("📊 Chart Settings")
    
    # Chart theme
    chart_theme = st.sidebar.selectbox(
        "Chart Theme",
        options=["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"],
        index=2 if dark_mode else 1
    )
    
    st.session_state.chart_theme = chart_theme
    
    # Animation settings
    st.session_state.enable_animations = st.sidebar.checkbox("✨ Enable Animations", value=True)
    
    # Performance settings
    st.sidebar.subheader("⚡ Performance")
    st.session_state.max_data_points = st.sidebar.slider(
        "Max Chart Data Points", 
        min_value=50, 
        max_value=500, 
        value=150,
        help="Reduce for better performance on slower devices"
    )


def get_theme_config() -> Dict[str, Any]:  # type: ignore
    """Get current theme configuration."""
    return {
        'dark_mode': st.session_state.get('dark_mode', False),
        'chart_theme': st.session_state.get('chart_theme', 'plotly_white'),
        'enable_animations': st.session_state.get('enable_animations', True),
        'max_data_points': st.session_state.get('max_data_points', 150)
    }


def format_metric_card(title: str, value: str, delta: str = "", color: str = "blue") -> str:
    """Format a metric as an HTML card."""
    delta_html = ""
    if delta:
        delta_color = "#00ff88" if delta.startswith("+") else "#ff4444"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9em; margin-top: 5px;">{delta}</div>'
    
    return f"""
    <div class="crypto-card glow-effect">
        <div style="color: {color}; font-size: 0.9em; font-weight: 500; margin-bottom: 5px;">{title}</div>
        <div style="font-size: 1.8em; font-weight: bold; margin-bottom: 5px;">{value}</div>
        {delta_html}
    </div>
    """


def show_loading_spinner(text: str = "Loading...") -> None:
    """Show a loading spinner with custom styling."""
    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; padding: 20px;">
            <div style="
                border: 4px solid #f3f3f3;
                border-top: 4px solid #00d4aa;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            "></div>
            <span style="color: #888; font-size: 1.1em;">{text}</span>
        </div>
        <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def create_status_badge(status: str, is_positive: bool = True) -> str:
    """Create a status badge with appropriate styling."""
    color = "#00ff88" if is_positive else "#ff4444"
    bg_color = "rgba(0, 255, 136, 0.1)" if is_positive else "rgba(255, 68, 68, 0.1)"
    
    return f"""
    <span style="
        background-color: {bg_color};
        color: {color};
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        border: 1px solid {color};
    ">{status}</span>
    """
