# Installation Guide for OctoBot-Trading with WEEX Exchange

This installation guide covers how to properly install OctoBot-Trading with custom dependencies including WEEX exchange support.

## 🚀 Quick Installation

### Option 1: Using the Installation Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/Danijel-Enoch/OctoBot-Trading.git
cd OctoBot-Trading

# Run the installation script
python install_dependencies.py

# Install the package itself in development mode
pip install -e .
```

### Option 2: Manual Installation

```bash
# 1. Install custom dependencies first
pip install git+https://github.com/Danijel-Enoch/trading-backend.git
pip install git+https://github.com/Danijel-Enoch/ccxt.git@master#subdirectory=python

# 2. Install standard dependencies
pip install -r setup_requirements.txt

# 3. Install the package
pip install -e .
```

### Option 3: Using requirements.txt (For Development)

If you're developing locally and want to use the original requirements.txt:

```bash
# Install from requirements.txt (includes Git dependencies)
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## 📦 What Gets Installed

### Custom Dependencies
- **trading-backend**: Custom trading backend from https://github.com/Danijel-Enoch/trading-backend
- **ccxt**: Custom CCXT with WEEX exchange support from https://github.com/Danijel-Enoch/ccxt

### Standard Dependencies
- numpy==1.26.3
- OctoBot-Backtesting>=1.9, <1.10
- Async-Channel>=2.2, <2.3
- OctoBot-Commons>=1.9.82, <1.10
- OctoBot-Tentacles-Manager>=2.9, <2.10
- cryptography
- sortedcontainers==2.4.0
- tinydb==4.5.2
- cachetools>=5.5.0, <6

## 🔧 Troubleshooting

### Problem: `setup.py egg_info` fails with Git URLs

**Solution**: Use the installation script or manual installation method instead of trying to install directly with `pip install git+https://github.com/...`.

### Problem: Dependency conflicts

**Solution**: Use a fresh virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
python install_dependencies.py
pip install -e .
```

### Problem: WEEX exchange not found

**Verification**: After installation, verify WEEX is available:

```python
import octobot_trading.constants as constants
print("weex" in constants.TESTED_EXCHANGES)  # Should print True

from octobot_trading.exchanges.implementations import WeexExchange
print(WeexExchange.get_name())  # Should print "weex"
```

## 🌟 WEEX Exchange Features

Once installed, you'll have access to:

- ✅ WEEX REST API integration
- ✅ WEEX WebSocket real-time data
- ✅ Spot trading support
- ✅ Order management (market, limit, stop-loss, take-profit)
- ✅ Account balance tracking
- ✅ Trade history and fills
- ✅ WebSocket feeds for ticker, orderbook, trades, and user data

## 📋 Verify Installation

Run this verification script to ensure everything is working:

```python
#!/usr/bin/env python3
"""Verification script for OctoBot-Trading with WEEX"""

try:
    # Test imports
    from octobot_trading.exchanges.implementations import WeexExchange, WeexWebSocketExchange
    import octobot_trading.constants as constants
    
    print("✅ Successfully imported WEEX exchange implementations")
    print(f"✅ WEEX in tested exchanges: {'weex' in constants.TESTED_EXCHANGES}")
    print(f"✅ WEEX REST exchange name: {WeexExchange.get_name()}")
    print(f"✅ WEEX WebSocket exchange name: {WeexWebSocketExchange.get_name()}")
    print("🎉 Installation verified successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please check your installation.")
except Exception as e:
    print(f"❌ Error: {e}")
```

## 🚀 Next Steps

After successful installation:

1. Configure your WEEX API credentials
2. Set up your trading configuration
3. Test with paper trading first
4. Deploy with your trading strategies

For more information, see the main README.md and WARP.md files.
