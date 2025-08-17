"""Data models and type definitions for the crypto dashboard."""

from typing import Dict, List, Optional, TypedDict, Protocol
from dataclasses import dataclass
import time


class PriceData(TypedDict):
    """Type definition for real-time price data."""
    price: float
    change: float
    timestamp: float


class ChartBuffer(TypedDict):
    """Type definition for chart buffer data."""
    t: List[float]  # timestamps
    p: List[float]  # prices


@dataclass
class ConnectionState:
    """WebSocket connection state management."""
    status: str = "Disconnected"
    symbol: Optional[str] = None
    last_update: float = 0.0
    error_count: int = 0
    
    @property
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.status == "Connected"
    
    @property
    def is_stale(self, timeout: float = 30.0) -> bool:
        """Check if connection is stale."""
        return time.time() - self.last_update > timeout


class PriceStreamProtocol(Protocol):
    """Protocol for price stream implementations."""
    
    def start(self, symbol: str) -> None:
        """Start streaming for a symbol."""
        ...
    
    def stop(self) -> None:
        """Stop the stream."""
        ...
    
    def get_latest_price(self) -> Optional[float]:
        """Get the most recent price."""
        ...
    
    def get_series(self) -> tuple[List[float], List[float]]:
        """Get timestamp and price series."""
        ...


class SessionStateManager:
    """Type-safe session state management."""
    
    @staticmethod
    def get_websocket_data() -> Dict[str, PriceData]:
        """Get WebSocket data with proper typing."""
        import streamlit as st
        if "websocket_data" not in st.session_state:
            st.session_state.websocket_data = {}
        return st.session_state.websocket_data  # type: ignore
    
    @staticmethod
    def get_chart_buffer() -> Dict[str, ChartBuffer]:
        """Get chart buffer with proper typing."""
        import streamlit as st
        if "chart_buffer" not in st.session_state:
            st.session_state.chart_buffer = {}
        return st.session_state.chart_buffer  # type: ignore
    
    @staticmethod
    def get_connection_state() -> ConnectionState:
        """Get connection state with proper typing."""
        import streamlit as st
        if "connection_state" not in st.session_state:
            st.session_state.connection_state = ConnectionState()
        return st.session_state.connection_state
    
    @staticmethod
    def get_price_stream() -> Optional[PriceStreamProtocol]:
        """Get price stream with proper typing."""
        import streamlit as st
        return getattr(st.session_state, "price_stream", None)


def format_price_adaptive(price: Optional[float]) -> str:
    """Format price with adaptive decimal places."""
    if price is None:
        return "Loading..."
    
    try:
        price_val = float(price)
        if price_val >= 100:
            return f"${price_val:.2f}"
        elif price_val >= 1:
            return f"${price_val:.4f}"
        else:
            return f"${price_val:.8f}"
    except (ValueError, TypeError):
        return "Invalid"


def format_change(change: Optional[float]) -> str:
    """Format price change percentage."""
    if change is None:
        return "Loading..."
    
    try:
        change_val = float(change)
        return f"{change_val:+.2f}%"
    except (ValueError, TypeError):
        return "Invalid"
