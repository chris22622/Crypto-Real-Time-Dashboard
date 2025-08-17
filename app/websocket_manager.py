"""Professional WebSocket manager for real-time crypto price streaming."""

import asyncio
import json
import logging
import threading
import time
from typing import Dict, List, Optional, Callable, Any
from collections import deque
import websockets

from models import ConnectionState, SessionStateManager

logger = logging.getLogger(__name__)


class WebSocketManager:
    """High-performance WebSocket manager with proper error handling and lifecycle management."""
    
    def __init__(self, max_price_history: int = 600, update_callback: Optional[Callable[[str, float, float], None]] = None):
        """
        Initialize WebSocket manager.
        
        Args:
            max_price_history: Maximum number of price points to keep in memory
            update_callback: Optional callback for price updates
        """
        self.max_price_history = max_price_history
        self.update_callback = update_callback
        
        # Thread-safe price data storage
        self._price_history: deque[tuple[float, float]] = deque(maxlen=max_price_history)
        self._current_price: Optional[float] = None
        self._connection_state = ConnectionState()
        
        # Threading management
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._stop_event: Optional[asyncio.Event] = None
        self._websocket: Any = None
        self._running = False
        
        # Performance metrics
        self._message_count = 0
        self._start_time = time.time()
        
    @property
    def is_running(self) -> bool:
        """Check if WebSocket is currently running."""
        return self._running and self._connection_state.is_connected
    
    @property
    def connection_state(self) -> ConnectionState:
        """Get current connection state."""
        return self._connection_state
    
    @property
    def message_count(self) -> int:
        """Get total message count."""
        return self._message_count
    
    @property
    def uptime(self) -> float:
        """Get connection uptime in seconds."""
        return time.time() - self._start_time
    
    def start(self, symbol: str) -> None:
        """
        Start WebSocket connection for a symbol.
        
        Args:
            symbol: Trading pair symbol (will be converted to lowercase)
        """
        if self._running and self._connection_state.symbol == symbol.lower():
            logger.info(f"WebSocket already running for {symbol}")
            return
        
        # Stop existing connection
        self.stop()
        
        # Initialize new connection
        self._connection_state = ConnectionState(
            status="Connecting",
            symbol=symbol.lower(),
            last_update=time.time()
        )
        
        self._running = True
        self._start_time = time.time()
        self._message_count = 0
        self._price_history.clear()
        
        # Start in background thread
        self._thread = threading.Thread(
            target=self._run_websocket,
            args=(symbol.lower(),),
            daemon=True,
            name=f"WebSocket-{symbol}"
        )
        self._thread.start()
        
        logger.info(f"Started WebSocket manager for {symbol.upper()} (stream: {symbol.lower()})")
    
    def stop(self) -> None:
        """Stop WebSocket connection gracefully."""
        if not self._running:
            return
        
        logger.info("Stopping WebSocket manager...")
        self._running = False
        self._connection_state.status = "Disconnecting"
        
        # Signal stop to async event loop
        if self._loop and not self._loop.is_closed() and self._stop_event:
            try:
                self._loop.call_soon_threadsafe(self._stop_event.set)
            except RuntimeError:
                pass  # Event loop may be closed
        
        # Reset state
        self._connection_state.status = "Disconnected"
        self._connection_state.symbol = None
        self._websocket = None
        
        logger.info("WebSocket manager stopped")
    
    def get_latest_price(self) -> Optional[float]:
        """Get the most recent price."""
        return self._current_price
    
    def get_series(self) -> tuple[List[float], List[float]]:
        """
        Get time series data.
        
        Returns:
            Tuple of (timestamps, prices) lists
        """
        if not self._price_history:
            return [], []
        
        timestamps, prices = zip(*self._price_history)
        return list(timestamps), list(prices)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get detailed connection information."""
        return {
            "status": self._connection_state.status,
            "symbol": self._connection_state.symbol,
            "is_connected": self._connection_state.is_connected,
            "message_count": self._message_count,
            "uptime": self.uptime,
            "last_update": self._connection_state.last_update,
            "price_history_length": len(self._price_history),
            "current_price": self._current_price
        }
    
    def _run_websocket(self, symbol: str) -> None:
        """Run WebSocket in dedicated event loop."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._stop_event = asyncio.Event()
        
        try:
            self._loop.run_until_complete(self._websocket_handler(symbol))
        except Exception as e:
            logger.error(f"WebSocket event loop error: {e}")
            self._connection_state.status = "Error"
            self._connection_state.error_count += 1
        finally:
            try:
                self._loop.close()
            except Exception:
                pass
            self._loop = None
            self._stop_event = None
    
    async def _websocket_handler(self, symbol: str) -> None:
        """Handle WebSocket connection with automatic reconnection."""
        uri = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
        backoff = 1.0
        max_backoff = 30.0
        
        while self._running and not (self._stop_event and self._stop_event.is_set()):
            try:
                logger.info(f"Connecting to WebSocket: {uri}")
                self._connection_state.status = "Connecting"
                
                async with websockets.connect(
                    uri,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10
                ) as websocket:
                    self._websocket = websocket
                    self._connection_state.status = "Connected"
                    self._connection_state.last_update = time.time()
                    backoff = 1.0  # Reset backoff on successful connection
                    
                    logger.info(f"WebSocket connected for {symbol.upper()}")
                    
                    await self._message_handler(websocket, symbol)
                    
            except websockets.exceptions.ConnectionClosedError:
                if self._running:
                    logger.warning(f"WebSocket connection closed for {symbol}, reconnecting...")
                    self._connection_state.status = "Reconnecting"
                else:
                    break
                    
            except Exception as e:
                if self._running:
                    logger.error(f"WebSocket error for {symbol}: {e}")
                    self._connection_state.status = "Error"
                    self._connection_state.error_count += 1
                    
                    # Exponential backoff
                    try:
                        await asyncio.wait_for(
                            self._stop_event.wait() if self._stop_event else asyncio.sleep(backoff), 
                            timeout=backoff
                        )
                        break  # Stop event was set
                    except asyncio.TimeoutError:
                        backoff = min(backoff * 2, max_backoff)
                else:
                    break
        
        self._connection_state.status = "Disconnected"
        logger.info(f"WebSocket handler finished for {symbol}")
    
    async def _message_handler(self, websocket: Any, symbol: str) -> None:
        """Handle incoming WebSocket messages."""
        async for message in websocket:
            if not self._running or (self._stop_event and self._stop_event.is_set()):
                break
            
            try:
                data = json.loads(message)
                price = float(data["p"])
                timestamp = data["T"] / 1000  # Convert to seconds
                
                # Update internal state
                self._current_price = price
                self._price_history.append((timestamp, price))
                self._message_count += 1
                self._connection_state.last_update = time.time()
                
                # Update session state through callback
                if self.update_callback:
                    self.update_callback(symbol.upper(), price, timestamp)
                
                # Log progress (first message and every 100th)
                if self._message_count == 1 or self._message_count % 100 == 0:
                    logger.info(f"WebSocket: {symbol.upper()} ${price:.8f} (msg #{self._message_count})")
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Error parsing WebSocket message for {symbol}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error processing message for {symbol}: {e}")
                break


# Global WebSocket manager instance
_websocket_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Get or create the global WebSocket manager instance."""
    global _websocket_manager
    
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager(update_callback=_update_session_state)
    
    return _websocket_manager


def _update_session_state(symbol: str, price: float, timestamp: float) -> None:
    """Update Streamlit session state with new price data."""
    try:
        # Update WebSocket data
        websocket_data = SessionStateManager.get_websocket_data()
        websocket_data[symbol] = {
            "price": price,
            "change": websocket_data.get(symbol, {}).get("change", 0.0),  # Preserve existing change
            "timestamp": time.time()
        }
        
        # Update chart buffer
        chart_buffer = SessionStateManager.get_chart_buffer()
        if symbol not in chart_buffer:
            chart_buffer[symbol] = {"t": [], "p": []}
        
        buf = chart_buffer[symbol]
        buf["t"].append(timestamp)
        buf["p"].append(price)
        
        # Keep last 600 points
        buf["t"] = buf["t"][-600:]
        buf["p"] = buf["p"][-600:]
        
    except Exception as e:
        logger.error(f"Error updating session state: {e}")
