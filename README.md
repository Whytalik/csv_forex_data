# 📊 Forex Data Analytics

![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/forex-data-analytics)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> 🚀 Advanced Forex Market Analysis Tool

This project processes and analyzes Forex (Foreign Exchange) market data to calculate various market metrics and indicators. It processes raw minute-by-minute price data, creates different timeframes, and calculates complex market metrics.

## 🏗️ Project Structure

```
src/
├── app/              # Main application code
├── config/           # Configuration files
├── data/             # Data storage
│   ├── raw/         # Raw minute data
│   ├── processed/    # Merged data files
│   ├── formatted/    # Reformatted data
│   └── timeframes/   # Different timeframe data
├── services/         # Core services
└── scripts/          # Utility scripts
```

## ✨ Features

### 🔄 Data Processing
  - 📈 Processes raw M1 (1-minute) Forex data
  - 🔄 Merges yearly data files
  - ⏰ Creates multiple timeframes (5m, 15m, 1h, 4h, 1d, 1w)
  - 🌍 Handles data in UTC+0 format with proper forex day alignment (21:00 UTC start)

### 📊 Market Analysis
  - Volatility & Range Metrics
  - Session-based Analysis (Asia, Frankfurt, London, NY)
  - High/Low Distribution Analysis
  - Intraday Pattern Analysis
  - Daily/Weekly Statistics

- **Integration**
  - Notion API integration for storing metrics
  - Multiple profile support

## 💱 Supported Currency Pairs

| Currency Pair | Description |
|--------------|-------------|
| 💶 EUR/USD | Euro vs US Dollar |
| 💷 GBP/USD | British Pound vs US Dollar |
| 💴 USD/JPY | US Dollar vs Japanese Yen |
| 🏦 USD/CHF | US Dollar vs Swiss Franc |
| 🥈 XAG/USD | Silver vs US Dollar |

## ⏰ Market Sessions (UTC)

- Asia: 21:00 - 03:00
- Frankfurt: 06:00 - 14:00
- London: 07:00 - 15:00
- Lunch: 11:00 - 12:00
- NY: 12:00 - 20:00

## Calculated Metrics

### 📏 Volatility & Range Metrics
| Metric | Description |
|--------|-------------|
| 📊 Average Daily Range | Mean trading range over 24h period |
| 📈 Average Daily Body Size | Mean candlestick body size |
| 📉 Average Weekly Range | Mean weekly high-low range |
| 📊 Average Weekly Body Size | Mean weekly candlestick body |
| 🕒 Session Ranges | Range analysis per trading session |

### 🎯 Session Distribution Analysis
| Session | Metrics |
|---------|---------|
| 🌏 Asia | High/Low probabilities, Range dominance |
| 🏛️ Frankfurt | Price action patterns, Session influence |
| 🎡 London | Major moves, Trend initiation |
| 🗽 NY | Momentum continuation, Reversal patterns |

### 📊 Pattern Recognition
| Pattern Type | Analysis |
|-------------|-----------|
| 📈 Bullish | Session-specific success rates |
| 📉 Bearish | Historical pattern completion |
| 🔄 Reversals | Key level identification |
| ➡️ Continuation | Momentum analysis |

### 📆 Time-Based Statistics
| Period | Analysis |
|--------|-----------|
| 📅 Daily | Session dominance, Range distribution |
| 📊 Weekly | Pattern frequency, Success rates |
| 🕒 Intraday | Time-specific opportunities |

## 🛠️ Requirements

### Dependencies
| Package | Version | Purpose |
|---------|---------|----------|
| 🐼 pandas | ≥2.0.0 | Data manipulation |
| 🔢 numpy | ≥1.24.0 | Numerical operations |
| 🌐 httpx | ≥0.24.0 | HTTP client |
| 📝 python-dotenv | ≥1.0.0 | Environment management |
| 🔄 aiohttp | ≥3.8.0 | Async HTTP |
| ⚡ asyncio | ≥3.4.3 | Async operations |

### System Requirements
- 💻 Python 3.10 or higher
- 🗄️ 16GB RAM recommended
- 💾 ~100GB free space (for historical data)

## 🚀 Setup

1. 📥 Clone the repository
```bash
git clone https://github.com/yourusername/forex-data-analytics.git
cd forex-data-analytics
```

2. 📦 Install dependencies:
```bash
pip install -r requirements.txt
```

3. ⚙️ Configure settings:
   - Update `config/settings.py` with your data paths
   - Configure Notion API settings in `config/notion_settings.py`

4. 🏃‍♂️ Run the application:
```bash
python src/app/main.py
```

## 📥 Data Requirements

### CSV Format Structure
```
╔════════════════╦═══════╦══════╦═══════╦═══════╦════════╗
║ DateTime       ║ Open  ║ High ║ Low   ║ Close ║ Volume ║
╠════════════════╬═══════╬══════╬═══════╬═══════╬════════╣
║ YYYYMMDD HHMM  ║ price ║ max  ║ min   ║ price ║   0    ║
╚════════════════╩═══════╩══════╩═══════╩═══════╩════════╝
```

### Example Data
```csv
20240101 170000;1.104270;1.104290;1.104250;1.104290;0
```

### Data Specifications
- 📅 Timestamp format: `YYYYMMDD HHMMSS`
- 💹 Price format: Decimal with 6 digits precision
- 🕒 Time zone: UTC+0 (GMT)
- 📊 Timeframe: M1 (1-minute)

## 🤝 Contributing

Feel free to submit issues and enhancement requests! Check our [Contributing Guidelines](CONTRIBUTING.md) for more information.

## 📝 TODO

- [ ] 🎯 Implement advanced pattern recognition
- [ ] 💱 Add more currency pairs
- [ ] 📊 Create visualization dashboard
- [ ] ✅ Add unit tests
- [ ] 📚 Add documentation for each metric calculation
- [ ] ⚡ Implement real-time data processing

## 📜 License

[MIT License](LICENSE)
