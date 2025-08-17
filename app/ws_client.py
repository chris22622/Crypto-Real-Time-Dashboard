"""WebSocket client for real-time crypto price streaming."""

import asyncio
import json
import logging
import threading
import time
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

import websockets

logger = logging.getLogger(__name__)

# Global variable to store session state updates
_session_state_updates: Dict[str, Any] = {}


class PriceStream:
    """WebSocket client for streaming real-time price data from Binance."""

    def __init__(self, max_points: int = 300):
        """
        Initialize price stream.

        Args:
            max_points: Maximum number of price points to keep in memory
        """
        self.max_points = max_points
        self.price_data = deque(maxlen=max_points)  # type: ignore
        self.current_symbol: Optional[str] = None
        self.websocket: Any = None
        self.running: bool = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        self.connection_task: Optional[asyncio.Task[Any]] = None  # type: ignore
        self._stop_event: Optional[asyncio.Event] = None

    async def _connect_and_stream(self, symbol: str) -> None:
        """
        Connect to WebSocket and stream price data.

        Args:
            symbol: Trading pair symbol (e.g., 'btcusdt')
        """
        uri = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@trade"
        backoff = 1
        max_backoff = 30

        while self.running and (not self._stop_event or not self._stop_event.is_set()):  # type: ignore
            try:
                logger.info(f"Attempting to connect to WebSocket for {symbol}")
                
                async with websockets.connect(uri) as websocket:
                    self.websocket = websocket
                    backoff = 1  # Reset backoff on successful connection
                    logger.info(f"Successfully connected to WebSocket for {symbol}")

                    try:
                        message_count = 0
                        async for message in websocket:
                            message_count += 1
                            # Check if we should stop
                            if not self.running or (self._stop_event and self._stop_event.is_set()):  # type: ignore
                                logger.info(f"Stopping WebSocket for {symbol} after {message_count} messages")
                                break

                            # Check if symbol changed
                            if self.current_symbol != symbol:
                                logger.info(f"Symbol changed from {symbol} to {self.current_symbol}, stopping connection")
                                break

                            try:
                                data = json.loads(message)
                                price = float(data["p"])
                                timestamp = data["T"] / 1000  # Convert to seconds
                                self.price_data.append((timestamp, price))
                                
                                # Log first message and every 100th message for debugging
                                if message_count == 1 or message_count % 100 == 0:
                                    logger.info(f"WebSocket received price for {symbol}: ${price:.6f} (msg #{message_count})")
                                
                                # Update global session state data
                                if symbol not in _session_state_updates:
                                    _session_state_updates[symbol] = {}
                                
                                _session_state_updates[symbol].update({
                                    'price': price,
                                    'timestamp': time.time(),
                                    'last_update': timestamp
                                })

                            except (json.JSONDecodeError, KeyError, ValueError) as e:
                                logger.warning(f"Error parsing message for {symbol}: {e}")
                                # Debug: log the problematic message (truncated)
                                logger.warning(f"Problematic message: {message[:100]}...")

                    except websockets.exceptions.ConnectionClosed:
                        if self.running and (not self._stop_event or not self._stop_event.is_set()) and self.current_symbol == symbol:  # type: ignore
                            logger.info(f"WebSocket connection closed for {symbol}, will reconnect")
                        else:
                            logger.info(f"WebSocket connection closed for {symbol}, not reconnecting (symbol changed or stopped)")
                        break

            except Exception as e:
                if self.running and (not self._stop_event or not self._stop_event.is_set()) and self.current_symbol == symbol:  # type: ignore
                    logger.error(f"WebSocket error for {symbol}: {e}")
                    logger.info(f"Reconnecting in {backoff} seconds...")
                    try:
                        if self._stop_event:
                            await asyncio.wait_for(self._stop_event.wait(), timeout=backoff)  # type: ignore
                        else:
                            await asyncio.sleep(backoff)
                        break  # Stop event was set during wait
                    except asyncio.TimeoutError:
                        pass  # Continue to reconnect
                    backoff = min(backoff * 2, max_backoff)
                else:
                    logger.info(f"Not reconnecting {symbol} - symbol changed or stopped")
                    break

        self.websocket = None
        logger.info(f"WebSocket connection ended for {symbol}")

    def _run_event_loop(self, symbol: str) -> None:
        """Run the event loop in a separate thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._stop_event = asyncio.Event()  # Create event in the correct event loop

        try:
            self.connection_task = self.loop.create_task(self._connect_and_stream(symbol))
            self.loop.run_until_complete(self.connection_task)  # type: ignore
        except asyncio.CancelledError:
            logger.info(f"WebSocket task cancelled for {symbol}")
        except Exception as e:
            logger.error(f"Event loop error: {e}")
        finally:
            try:
                # Cancel any remaining tasks
                if self.connection_task and not self.connection_task.done():  # type: ignore
                    self.connection_task.cancel()  # type: ignore
                
                # Close any remaining connections
                pending = asyncio.all_tasks(self.loop)
                if pending:
                    self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    
            except Exception as e:
                logger.debug(f"Error during cleanup: {e}")
            finally:
                self.loop.close()
                self.loop = None

    def start(self, symbol: str) -> None:
        """
        Start streaming price data for a symbol.

        Args:
            symbol: Trading pair symbol
        """
        if self.running and self.current_symbol == symbol:
            logger.info(f"Already streaming {symbol}")
            return

        # Stop any existing stream completely
        self.stop()
        
        # Wait for old thread to actually finish
        old_thread = self.thread
        if old_thread and old_thread.is_alive():
            old_thread.join(timeout=0.5)  # Brief wait for clean shutdown
        
        # Clear any residual state
        self.thread = None
        self.connection_task = None
        self.websocket = None

        # Set new symbol and start
        self.current_symbol = symbol
        self.running = True
        self.price_data.clear()

        # Start WebSocket in a separate thread
        self.thread = threading.Thread(
            target=self._run_event_loop, 
            args=(symbol,), 
            daemon=True,
            name=f"WebSocket-{symbol}"
        )
        self.thread.start()

        logger.info(f"Started price stream for {symbol}")

    def stop(self) -> None:
        """Stop the price stream."""
        if not self.running:
            return

        logger.info("Stopping price stream...")
        self.running = False

        # Signal the async task to stop (non-blocking)
        if self.loop and not self.loop.is_closed() and self._stop_event:
            try:
                # Create a coroutine to set the event
                async def set_stop_event():
                    if self._stop_event:
                        self._stop_event.set()
                
                # Don't wait for result, just schedule it
                asyncio.run_coroutine_threadsafe(set_stop_event(), self.loop)
            except (RuntimeError, asyncio.InvalidStateError):
                logger.debug("Could not signal stop event")

        # Force close websocket (non-blocking)
        if self.loop and not self.loop.is_closed():
            try:
                # Don't wait for result, just schedule cleanup
                asyncio.run_coroutine_threadsafe(self._cleanup(), self.loop)
            except (RuntimeError, asyncio.InvalidStateError):
                logger.debug("Could not schedule cleanup")

        # Reset state immediately (don't wait for thread)
        self.current_symbol = None
        self.websocket = None
        
        # Let the thread clean up in background
        if self.thread and self.thread.is_alive():
            # Just mark that we want to stop, let it finish naturally
            pass
        
        self.connection_task = None

        logger.info("Price stream stopped")

    async def _cleanup(self) -> None:
        """Clean up WebSocket connection."""
        if self.websocket:
            try:
                await self.websocket.close()
                await asyncio.sleep(0.1)  # Give time for connection to close
                logger.debug("WebSocket connection closed")
            except Exception as e:
                logger.debug(f"Error during websocket cleanup: {e}")
        
        # Cancel the connection task
        if self.connection_task and not self.connection_task.done():  # type: ignore
            self.connection_task.cancel()  # type: ignore
            try:
                await self.connection_task  # type: ignore
            except asyncio.CancelledError:
                pass

        self.websocket = None

    def get_series(self) -> Tuple[List[float], List[float]]:
        """
        Get current price series data.

        Returns:
            Tuple of (timestamps, prices) lists
        """
        if not self.price_data:
            return [], []

        data = list(self.price_data)
        timestamps, prices = zip(*data)
        return list(timestamps), list(prices)

    def get_latest_price(self) -> Optional[float]:
        """
        Get the most recent price.

        Returns:
            Latest price or None if no data
        """
        if not self.price_data:
            return None
        
        return self.price_data[-1][1]

    def get_price_change(self, window_seconds: int = 60) -> Optional[float]:
        """
        Get price change percentage over a time window.

        Args:
            window_seconds: Time window in seconds

        Returns:
            Price change percentage or None if insufficient data
        """
        if len(self.price_data) < 2:
            return None

        current_time = time.time()
        current_price = self.price_data[-1][1]

        # Find price from window_seconds ago
        for timestamp, price in reversed(self.price_data):
            if current_time - timestamp >= window_seconds:
                return ((current_price - price) / price) * 100

        return None

def get_websocket_updates() -> Dict[str, Any]:
    """
    Get and clear pending WebSocket session state updates.
    
    Returns:
        Dictionary of symbol -> update data
    """
    global _session_state_updates
    updates = _session_state_updates.copy()
    _session_state_updates.clear()
    return updates

def has_websocket_updates() -> bool:
    """
    Check if there are pending WebSocket updates.
    
    Returns:
        True if there are pending updates
    """
    return bool(_session_state_updates)
