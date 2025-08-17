"""Data sources for crypto prices from Binance API."""

import logging
from typing import Any, Dict, Optional, List
import time

import pandas as pd  # type: ignore
import requests
import streamlit as st  # type: ignore

logger = logging.getLogger(__name__)

BASE_URL = "https://api.binance.com/api/v3"


@st.cache_data(ttl=30)
def get_top_symbols(limit: int = 50) -> pd.DataFrame:
    """
    Fetch top cryptocurrency symbols from Binance 24hr ticker statistics.
    Enhanced for maximum accuracy and reliability.

    Args:
        limit: Maximum number of symbols to return

    Returns:
        DataFrame with columns: symbol, price, priceChangePercent, volume, trades, high, low, marketCap
    """
    try:
        logger.info(f"Fetching top {limit} crypto symbols from Binance API...")
        
        # Add retry logic for reliability
        max_retries = 3
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"{BASE_URL}/ticker/24hr", 
                    timeout=15,
                    headers={'User-Agent': 'CryptoDashboard/1.0'}
                )
                response.raise_for_status()
                break
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(1)
        
        if response is None:
            raise requests.RequestException("Failed to get response after retries")
            
        data = response.json()
        logger.info(f"Successfully fetched data for {len(data)} trading pairs")

        # Enhanced filtering for USDT pairs with better validation
        usdt_pairs: List[Dict[str, Any]] = []
        excluded_symbols = {'USDCUSDT', 'BUSDUSDT', 'TUSDUSDT', 'USTCUSDT'}  # Exclude stablecoins
        
        for item in data:
            symbol = item["symbol"]
            if (symbol.endswith("USDT") and 
                symbol not in excluded_symbols and
                float(item["volume"]) > 0 and  # Ensure active trading
                float(item["lastPrice"]) > 0):  # Ensure valid price
                usdt_pairs.append(item)

        if not usdt_pairs:
            logger.error("No valid USDT pairs found")
            return pd.DataFrame()

        logger.info(f"Found {len(usdt_pairs)} valid USDT trading pairs")

        # Create enhanced DataFrame with more data points
        df = pd.DataFrame(usdt_pairs)
        
        # Select and rename columns for comprehensive data
        column_mapping = {
            "symbol": "symbol",
            "lastPrice": "price", 
            "priceChangePercent": "priceChangePercent",
            "volume": "volume",
            "count": "trades",
            "highPrice": "high24h",
            "lowPrice": "low24h",
            "openPrice": "open24h",
            "prevClosePrice": "prevClose",
            "weightedAvgPrice": "avgPrice",
            "quoteVolume": "quoteVolume"
        }
        
        # Ensure all required columns exist
        available_columns = [col for col in column_mapping.keys() if col in df.columns]
        df_selected = df[available_columns].copy()
        df_selected = df_selected.rename(columns={k: column_mapping[k] for k in available_columns})

        # Convert to appropriate types with error handling
        numeric_columns = ['price', 'priceChangePercent', 'volume', 'trades']
        if 'high24h' in df_selected.columns:
            numeric_columns.extend(['high24h', 'low24h', 'open24h', 'prevClose', 'avgPrice', 'quoteVolume'])
            
        for col in numeric_columns:
            if col in df_selected.columns:
                df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce')  # type: ignore

        # Remove any rows with invalid data
        df_selected = df_selected.dropna(subset=['price', 'volume'])  # type: ignore
        df_selected = df_selected[df_selected['price'] > 0]
        df_selected = df_selected[df_selected['volume'] > 0]

        # Add computed fields for better analysis
        if 'high24h' in df_selected.columns and 'low24h' in df_selected.columns:
            df_selected['volatility'] = ((df_selected['high24h'] - df_selected['low24h']) / df_selected['low24h'] * 100)
        
        # Estimate market cap (volume * price as proxy)
        df_selected['marketCapProxy'] = df_selected['volume'] * df_selected['price']

        # Sort by volume (most actively traded first) and return top N
        df_selected = df_selected.sort_values("volume", ascending=False).head(limit)  # type: ignore
        df_selected = df_selected.reset_index(drop=True)  # type: ignore

        # Add ranking
        df_selected['rank'] = range(1, len(df_selected) + 1)

        logger.info(f"Successfully processed {len(df_selected)} symbols")
        return df_selected

    except requests.RequestException as e:
        logger.error(f"Network error fetching top symbols: {e}")
        st.error(f"🌐 Network Error: {e}")
        return pd.DataFrame()
    except ValueError as e:
        logger.error(f"Data parsing error: {e}")
        st.error(f"📊 Data Error: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error fetching top symbols: {e}")
        st.error(f"❌ Unexpected Error: {e}")
        return pd.DataFrame()


def get_symbol_price(symbol: str) -> Optional[float]:
    """
    Get current price for a specific symbol with enhanced reliability.

    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')

    Returns:
        Current price as float, or None if error
    """
    try:
        symbol = symbol.upper().strip()
        
        # Add retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"{BASE_URL}/ticker/price", 
                    params={"symbol": symbol}, 
                    timeout=10,
                    headers={'User-Agent': 'CryptoDashboard/1.0'}
                )
                response.raise_for_status()
                data = response.json()
                
                price = float(data["price"])
                if price <= 0:
                    logger.warning(f"Invalid price for {symbol}: {price}")
                    return None
                    
                return price
                
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}, retrying...")
                time.sleep(0.5)

    except (requests.RequestException, ValueError, KeyError) as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return None


def get_multiple_symbol_prices(symbols: List[str]) -> Dict[str, Optional[float]]:
    """
    Get current prices for multiple symbols efficiently.

    Args:
        symbols: List of trading pair symbols

    Returns:
        Dictionary mapping symbols to prices
    """
    try:
        # Use batch API for efficiency
        response = requests.get(f"{BASE_URL}/ticker/price", timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Create lookup dictionary
        price_lookup = {item["symbol"]: float(item["price"]) for item in data}
        
        # Return prices for requested symbols
        result: Dict[str, Optional[float]] = {}
        for symbol in symbols:
            symbol_upper = symbol.upper().strip()
            result[symbol] = price_lookup.get(symbol_upper)
            
        return result
        
    except Exception as e:
        logger.error(f"Error fetching multiple prices: {e}")
        return {symbol: None for symbol in symbols}


def get_symbol_info(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get symbol information including filters and trading rules.

    Args:
        symbol: Trading pair symbol

    Returns:
        Symbol info dict or None if error
    """
    try:
        response = requests.get(f"{BASE_URL}/exchangeInfo", timeout=10)
        response.raise_for_status()
        data = response.json()

        for sym_info in data["symbols"]:
            if sym_info["symbol"] == symbol.upper():
                return sym_info

        return None

    except requests.RequestException as e:
        logger.error(f"Error fetching symbol info for {symbol}: {e}")
        return None
