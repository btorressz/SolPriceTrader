#  📉 SolPriceTrader - SOL/USDC Mean Reversion Trading Simulator

## 📄 Overview

This is a **Python-based trading simulator** that implements a **mean reversion strategy** for SOL/USDC cryptocurrency trading.  
The application fetches real-time price data from the Jupiter API, executes trades based on **moving average crossovers**, and provides real-time visualization of trading performance.

---

## 🏛️ System Architecture

The application follows a **modular architecture** with clear separation of concerns:

### 🗄️ Data Layer
- Jupiter API integration for real-time SOL/USDC price feeds

### ⚙️ Trading Logic
- Mean reversion strategy implementation with moving averages

### 💼 Portfolio Management
- Cash and position tracking with P&L calculations

### 📊 Visualization
- Real-time **matplotlib** charts for price action and performance

### 🔧 Utilities
- Helper functions for calculations and formatting

---

## 🗂️ Key Components

### 🔗 1. Data Fetching (`data_fetcher.py`)
- **Purpose:** Integrates with Jupiter API to fetch SOL/USDC price quotes
- **Implementation:** RESTful API calls with rate limiting (1-second intervals)
- **Configuration:** Uses SOL and USDC mint addresses for accurate pricing
- **Error Handling:** Includes retry logic and graceful degradation

### ⚙️ 2. Trading Simulator (`trading_simulator.py`)
- **Purpose:** Main orchestrator implementing mean reversion strategy
- **Strategy:** Buys when price is below moving average, sells when above
- **Parameters:** Configurable MA period (default 20), fetch interval (30s), slippage (0.1%)
- **Logging:** CSV file generation for trade history and analysis

### 💼 3. Portfolio Management (`portfolio.py`)
- **Purpose:** Tracks cash balance, SOL holdings, and calculates P&L
- **Features:** Cost basis tracking, position sizing, and performance metrics
- **Risk Management:** Validates trades against available cash/holdings

### 📈 4. Visualization (`visualizer.py`)
- **Purpose:** Real-time **matplotlib** charts for monitoring trading activity
- **Charts:** Price/MA overlay with trade markers, cumulative P&L tracking
- **Updates:** Live chart updates with new data points

### 🔧 5. Utilities (`utils.py`)
- **Purpose:** Common calculations and formatting functions
- **Functions:** Moving averages, currency formatting, percentage calculations
- **Design:** Reusable components to avoid code duplication

---

## 🔄 Data Flow

1. **Price Collection:** Jupiter API fetched every 30 seconds for SOL/USDC quotes.
2. **Strategy Evaluation:** New prices compared against 20-period moving average.
3. **Trade Execution:** Buy/sell decisions based on mean reversion signals.
4. **Portfolio Update:** Cash and holdings adjusted with slippage costs.
5. **Visualization:** Charts updated with new price data and trade markers.
6. **Logging:** Trade details recorded to CSV for analysis.

---


## 📦 External Dependencies

### 🧰 Core Dependencies
- **requests:** HTTP client for Jupiter API integration
- **matplotlib:** Real-time charting and visualization
- **numpy:** Numerical calculations and data processing

### 🌐 Jupiter API Integration
- **Endpoint:** `https://quote-api.jup.ag/v6/quote`
- **Rate Limiting:** 1-second minimum intervals between requests
- **Slippage:** 0.5% default tolerance for realistic pricing

### ⚙️ System Dependencies (via Nix)
- Python 3.11 runtime environment
- Graphics libraries (**Cairo**, **GTK3**) for matplotlib rendering
- Media processing tools (**FFmpeg**) for potential chart exports

---

## 🚀 Deployment Strategy

### 🧪 Development Environment
- **Runtime:** Python 3.11 with automatic dependency installation
- **Execution:** Single command launch via workflow configuration

### 🏭 Production Considerations
- **Scalability:** Single-threaded design suitable for personal trading simulation
- **Monitoring:** CSV logging provides audit trail for performance analysis
- **Extensibility:** Modular design allows easy strategy modifications

### ⚙️ Configuration Management
- **Parameters:** Hardcoded defaults with easy modification points
- **Environment:** Self-contained setup with minimal external requirements
- **Data Storage:** Local CSV files for trade history persistence

  ---


  ## 🧾📜 LICENSE
  - This project is under the **MIT LICENSE**

     ---

  

  
