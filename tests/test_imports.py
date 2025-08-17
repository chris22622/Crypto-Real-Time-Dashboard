"""Test imports to ensure all modules load correctly."""


def test_imports():
    """Test that all app modules can be imported without errors."""
    assert True


def test_data_sources():
    """Test data sources module functions."""
    from app.data_sources import get_symbol_price, get_top_symbols

    # Test that functions exist and are callable
    assert callable(get_top_symbols)
    assert callable(get_symbol_price)


def test_utils():
    """Test utility functions."""
    from app.utils import format_percentage, format_price, format_volume

    # Test price formatting
    assert format_price(1.23456789) == "$1.2346"
    assert format_price(1234.56) == "$1,234.56"

    # Test percentage formatting
    assert format_percentage(5.67) == "+5.67%"
    assert format_percentage(-3.21) == "-3.21%"

    # Test volume formatting
    assert format_volume(1500000) == "1.50M"
    assert format_volume(2500000000) == "2.50B"


def test_ws_client():
    """Test WebSocket client initialization."""
    from app.ws_client import PriceStream

    stream = PriceStream()
    assert stream.max_points == 300
    assert not stream.running
    assert stream.current_symbol is None
