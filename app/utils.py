"""Utility functions for data formatting and calculations."""

import time
from typing import Any, Callable, Optional


def format_price(price: float, decimals: int = 8) -> str:
    """
    Format price with appropriate decimal places.

    Args:
        price: Price value to format
        decimals: Maximum decimal places

    Returns:
        Formatted price string
    """
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.4f}"
    else:
        return f"${price:.{decimals}f}".rstrip("0").rstrip(".")


def format_percentage(percentage: float) -> str:
    """
    Format percentage with color indicators.

    Args:
        percentage: Percentage value

    Returns:
        Formatted percentage string
    """
    sign = "+" if percentage > 0 else ""
    return f"{sign}{percentage:.2f}%"


def format_volume(volume: float) -> str:
    """
    Format trading volume in readable format.

    Args:
        volume: Volume value

    Returns:
        Formatted volume string
    """
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.2f}K"
    else:
        return f"{volume:.2f}"


def get_color_for_change(change: float) -> str:
    """
    Get color for price change display.

    Args:
        change: Price change percentage

    Returns:
        Color string for styling
    """
    if change > 0:
        return "#00C851"  # Green
    elif change < 0:
        return "#FF4444"  # Red
    else:
        return "#CCCCCC"  # Gray


def calculate_price_change(current: float, previous: float) -> float:
    """
    Calculate percentage change between two prices.

    Args:
        current: Current price
        previous: Previous price

    Returns:
        Percentage change
    """
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100


def debounce(func: Callable[..., Any], wait_time: float) -> Callable[..., Any]:
    """
    Debounce function decorator to limit call frequency.

    Args:
        func: Function to debounce
        wait_time: Minimum time between calls in seconds

    Returns:
        Debounced function
    """
    last_called = 0

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal last_called
        now = time.time()
        if now - last_called >= wait_time:
            last_called = now
            return func(*args, **kwargs)

    return wrapper


def clean_symbol_name(symbol: str) -> str:
    """
    Clean symbol name for display.

    Args:
        symbol: Raw symbol (e.g., 'BTCUSDT')

    Returns:
        Cleaned symbol (e.g., 'BTC')
    """
    if symbol.endswith("USDT"):
        return symbol[:-4]
    elif symbol.endswith("BUSD"):
        return symbol[:-4]
    elif symbol.endswith("BTC"):
        return symbol[:-3]
    return symbol


def validate_alert_threshold(threshold: str, alert_type: str) -> Optional[float]:
    """
    Validate and parse alert threshold input.

    Args:
        threshold: Threshold value as string
        alert_type: Type of alert ('price' or 'percentage')

    Returns:
        Parsed threshold value or None if invalid
    """
    try:
        value = float(threshold.strip())

        if alert_type == "price" and value <= 0:
            return None
        elif alert_type == "percentage" and abs(value) > 100:
            return None

        return value
    except (ValueError, AttributeError):
        return None


def time_ago(timestamp: float) -> str:
    """
    Format timestamp as 'time ago' string.

    Args:
        timestamp: Unix timestamp

    Returns:
        Human-readable time ago string
    """
    now = time.time()
    diff = now - timestamp

    if diff < 60:
        return f"{int(diff)}s ago"
    elif diff < 3600:
        return f"{int(diff / 60)}m ago"
    elif diff < 86400:
        return f"{int(diff / 3600)}h ago"
    else:
        return f"{int(diff / 86400)}d ago"
