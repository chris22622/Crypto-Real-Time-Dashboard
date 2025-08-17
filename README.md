# 🚀 Crypto Real-Time Dashboard

[![CI](https://github.com/chris-leslie/crypto-realtime-dashboard/workflows/CI/badge.svg)](https://github.com/chris-leslie/crypto-realtime-dashboard/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

A sleek, production-ready Streamlit application that streams live cryptocurrency prices via WebSocket, displays market analytics, and provides real-time price alerts. Built for traders and crypto enthusiasts who need instant market insights.

## ✨ Features

- **📊 Live Market Data**: Real-time ticker table showing top cryptocurrencies with 24h changes and volume
- **📈 Interactive Charts**: Live sparkline charts with WebSocket streaming (1-second updates)
- **🔔 Smart Alerts**: Price target and percentage change alerts with instant notifications
- **🔍 Advanced Search**: Filter cryptocurrencies by symbol with instant results
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **⚡ High Performance**: Optimized WebSocket connections with automatic reconnection
- **🎨 Modern UI**: Clean, professional interface with color-coded price movements

## 🚀 Quickstart

```bash
# Clone the repository
git clone https://github.com/chris-leslie/crypto-realtime-dashboard.git
cd crypto-realtime-dashboard

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run app/main.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📸 Screenshots

> **Note**: Screenshots and demo GIFs are available in the [docs/screenshots](docs/screenshots) directory.

### Main Dashboard
![Main Dashboard](docs/screenshots/main_dashboard.png)
*Live cryptocurrency dashboard with real-time charts and market data*

### Live Price Chart
![Live Chart](docs/screenshots/live_chart.png)
*Real-time price sparkline with WebSocket streaming*

### Alert System
![Alert Notification](docs/screenshots/alert_notification.png)
*Instant price alerts with customizable thresholds*

## 🛠️ Technology Stack

- **Frontend**: Streamlit with Plotly for interactive charts
- **Backend**: Python 3.11 with asyncio for WebSocket handling
- **Data Sources**: Binance Public API (REST + WebSocket)
- **Real-time**: WebSocket streaming for live price updates
- **Visualization**: Plotly for responsive, interactive charts

## 📚 Documentation

- [📋 Architecture Overview](docs/ARCHITECTURE.md) - System design and data flow
- [📷 Screenshot Guide](docs/SHOTLIST.md) - Documentation screenshots
- [🔧 API Documentation](docs/API.md) - Binance API integration details

## 🚀 Deployment

### Streamlit Cloud
1. Fork this repository
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Select `app/main.py` as the main file
4. Deploy with one click!

### Render/Railway
```bash
# Add to your deployment platform
pip install -r requirements.txt
streamlit run app/main.py --server.port $PORT
```

### Docker
```bash
# Build the container
docker build -t crypto-dashboard .

# Run the container
docker run -p 8501:8501 crypto-dashboard
```

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set custom refresh rates
STREAMLIT_REFRESH_RATE=2  # seconds
STREAMLIT_MAX_DATA_POINTS=300
```

### Alert Settings
- **Price Targets**: Set alerts above/below specific price levels
- **Percentage Changes**: Monitor percentage moves over time windows (1min - 1hour)
- **Instant Notifications**: Browser notifications and in-app toasts

## 🧪 Development

### Setup Development Environment
```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black .
ruff check .

# Run tests
pytest -v
```

### Code Quality
- **Black**: Code formatting
- **Ruff**: Fast Python linting
- **Type Hints**: Full type annotation
- **Pre-commit**: Automated code quality checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## 📋 Roadmap

### Version 2.0
- [ ] Multi-symbol concurrent streaming
- [ ] Historical data charts (1D, 7D, 30D)
- [ ] Portfolio tracking and P&L calculation
- [ ] Email/Telegram alert notifications

### Version 3.0
- [ ] User authentication and saved preferences
- [ ] Advanced technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Social sentiment analysis integration
- [ ] Mobile app (React Native)

## 🐛 Bug Reports & Feature Requests

Please use the [GitHub Issues](https://github.com/chris-leslie/crypto-realtime-dashboard/issues) page to report bugs or request features.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Security

For security concerns, please review our [Security Policy](SECURITY.md) and report vulnerabilities responsibly.

## 📞 Support

- **Documentation**: Check the [docs](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/chris-leslie/crypto-realtime-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/chris-leslie/crypto-realtime-dashboard/discussions)

## ⭐ Acknowledgments

- [Binance](https://binance.com) for providing free public API access
- [Streamlit](https://streamlit.io) for the amazing web app framework
- [Plotly](https://plotly.com) for interactive charting capabilities

---

**Built with ❤️ by [Chrissano Leslie](https://github.com/chris-leslie)**

*Ready to trade? Start monitoring your favorite cryptocurrencies in real-time!*
