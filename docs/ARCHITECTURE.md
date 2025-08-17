# Architecture Overview

This document describes the architecture and data flow of the Crypto Real-Time Dashboard.

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    Data Layer    │    │   External      │
│   Frontend      │    │                  │    │   Services      │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • Main UI       │    │ • REST Client    │────│ Binance REST    │
│ • Components    │◄───│ • WebSocket      │    │ API (24h data)  │
│ • State Mgmt    │    │   Client         │    │                 │
│ • Auto-refresh  │    │ • Data Buffer    │    │ Binance         │
└─────────────────┘    │ • Alert Logic   │◄───│ WebSocket       │
                       └──────────────────┘    │ (Live trades)   │
                                               └─────────────────┘
```

## Data Flow

### 1. Initial Load
```
User opens app → Streamlit loads → Fetch top symbols (REST) → Display table
```

### 2. Symbol Selection
```
User selects symbol → Start WebSocket → Stream trades → Update chart
```

### 3. Real-time Updates
```
WebSocket receives trade → Add to deque buffer → Update chart → Check alerts
```

### 4. Alert Processing
```
New price data → Calculate change → Check thresholds → Trigger notification
```

## Component Details

### Frontend Layer (Streamlit)
- **main.py**: Application entry point, layout orchestration
- **ui_components.py**: Reusable UI components and rendering logic
- **Session State**: Manages WebSocket connections and user preferences

### Data Layer
- **data_sources.py**: REST API integration for market data
- **ws_client.py**: WebSocket client for real-time price streaming
- **utils.py**: Data formatting, calculations, and helper functions

### External Services
- **Binance REST API**: 24-hour ticker statistics, symbol information
- **Binance WebSocket**: Real-time trade stream for live price updates

## Key Technologies

### Core Stack
- **Python 3.11**: Runtime environment
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charting and visualization

### Real-time Communication
- **WebSockets**: Live price streaming from Binance
- **Asyncio**: Asynchronous WebSocket handling
- **Threading**: Non-blocking WebSocket operations

### Data Management
- **Collections.deque**: Circular buffer for price history
- **Requests**: HTTP client for REST API calls
- **JSON**: Data serialization and parsing

## Performance Considerations

### Memory Management
- Circular buffer (deque) limits memory usage for price history
- Configurable maximum data points (50-500 points)
- Automatic cleanup of old data

### Network Efficiency
- Single WebSocket connection per symbol
- Automatic reconnection with exponential backoff
- REST API caching with 30-second TTL

### UI Responsiveness
- Asynchronous WebSocket processing
- Configurable refresh rates (1-10 seconds)
- Non-blocking data updates

## Error Handling

### Network Failures
- Automatic WebSocket reconnection
- REST API timeout handling
- Graceful degradation when services unavailable

### Data Validation
- Price data type validation
- Symbol existence checking
- Alert threshold validation

### User Experience
- Loading states for API calls
- Error messages for failed operations
- Connection status indicators

## Security Considerations

### API Usage
- Uses only public Binance endpoints
- No authentication required
- Rate limiting handled by caching

### Data Privacy
- No user data collection
- No persistent storage of personal information
- All data processing happens client-side

## Scalability Notes

### Current Limitations
- Single symbol WebSocket stream at a time
- In-memory data storage only
- No historical data persistence

### Future Enhancements
- Multi-symbol concurrent streaming
- Database integration for historical data
- User accounts and personalized alerts
- Mobile app integration

## Development Workflow

### Code Quality
- Black code formatting
- Ruff linting and static analysis
- Type hints for better maintainability
- Comprehensive error handling

### Testing Strategy
- Unit tests for utility functions
- Integration tests for API clients
- UI component testing
- End-to-end workflow validation

### Deployment
- Streamlit Cloud integration
- Docker containerization support
- Environment-based configuration
- CI/CD pipeline with GitHub Actions
