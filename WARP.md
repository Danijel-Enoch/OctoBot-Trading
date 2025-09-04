# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

OctoBot-Trading is a Python trading library that provides core trading functionality for the OctoBot ecosystem. It handles exchange connections, order management, portfolio tracking, and trading execution for cryptocurrency exchanges. The library is built to support both live trading and backtesting scenarios.

## Core Architecture

### Key Components

**Exchange Management Layer**
- `ExchangeManager` - Central coordinator managing all exchange-related operations
- `AbstractExchange` - Base class for exchange implementations (CCXT-based)
- `ExchangePersonalData` - Manages user-specific data (orders, positions, portfolio)
- `ExchangeSymbolsData` - Handles market data and symbol information

**Trading System**
- `Trader` - Executes trades and manages order lifecycle
- `OrdersManager` - Tracks and manages all orders across their states
- `Order` - Individual order instances with state management
- `Portfolio` - Tracks balances and position values across exchanges

**Data Flow Architecture**
- Uses async channels for real-time data distribution
- Event-driven system with producers/consumers pattern
- Channels: Orders, Balance, Positions, Ticker, OrderBook, etc.
- WebSocket and REST API integration via CCXT

**Trading Modes**
- Scriptable trading strategies with DSL support
- Order groups for complex multi-order strategies
- Active order swap strategies and chained orders

### Key Design Patterns

**State Management**: Orders progress through defined states (PENDING_CREATION → OPEN → FILLED/CANCELED)

**Channel Architecture**: All data flows through typed channels with producers pushing updates to consumers

**Exchange Abstraction**: CCXT library provides unified interface to 100+ exchanges

**Async/Await**: Fully asynchronous for handling concurrent exchange operations

## Development Commands

### Build and Setup
```bash
# Install development dependencies
pip install -r dev_requirements.txt

# Build Cython extensions
make build

# Clean build artifacts
make clean
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=octobot_trading

# Run specific test file
pytest tests/personal_data/orders/test_orders_manager.py

# Run tests with specific markers
pytest -m "not slow"

# Run tests in parallel
pytest -n auto
```

### Linting and Code Quality
```bash
# Run pylint
pylint octobot_trading

# Run with specific config
pylint --rcfile=standard.rc octobot_trading

# Check specific files
pylint octobot_trading/personal_data/orders/order.py
```

### Package Management
```bash
# Build package
python setup.py sdist bdist_wheel

# Install in development mode
pip install -e .

# Update dependencies
pur -r requirements.txt
```

## Testing Strategy

### Test Structure
- Tests mirror source structure under `tests/` directory
- Simulated exchange managers for testing without real API calls
- Comprehensive order lifecycle and state transition testing
- Exchange adapter testing with mock responses

### Key Test Patterns
```python
# Use simulated_trader fixture for isolated testing
async def test_orders_manager(simulated_trader):
    config, exchange_manager, trader = simulated_trader
    orders_manager = exchange_manager.exchange_personal_data.orders_manager
```

### Exchange Testing
- Real exchange tests for supported exchanges (binance, kucoin, okx, etc.)
- Authenticated tests require API credentials
- Simulator mode for testing without real funds

## Working with Orders

### Order Lifecycle
1. **Creation**: `Order` instance created with `OrdersManager.upsert_order_from_raw()`
2. **Initialization**: Order state initialized, validation performed
3. **Submission**: Sent to exchange via `Trader.create_order()`
4. **Monitoring**: Status updates via exchange channels
5. **Completion**: Final state (FILLED/CANCELED) with cleanup

### Order Types and States
- **Market/Limit Orders**: Basic buy/sell orders
- **Stop Loss/Take Profit**: Risk management orders (often self-managed)
- **Chained Orders**: Orders created after parent order fills
- **Order Groups**: Multiple related orders with swap strategies

### Key Order Methods
```python
# Create order from exchange data
order = order_factory.create_order_instance_from_raw(trader, raw_order)

# Update order state
await order.update_from_raw(raw_order_data)

# Check order status
if order.is_filled():
    # Handle filled order
```

## Exchange Integration

### Supported Exchanges
- **Tested**: binance, kucoin, okx, coinbase, bybit, mexc, weex, etc.
- **Futures**: binanceusdm, bybit (default future exchanges)
- **Simulator**: All exchanges supported in simulation mode
- **WEEX**: Added native support for WEEX exchange with REST and WebSocket APIs

### Exchange Configuration
```python
# Exchange manager setup
exchange_manager = ExchangeManager(config, "binance")
await exchange_manager.initialize()

# Check exchange capabilities
supported_orders = exchange.get_supported_elements(
    enums.ExchangeSupportedElements.UNSUPPORTED_ORDERS
)
```

### CCXT Integration
- Version pinned to 4.5.0 for stability
- Custom exchange adapters extend AbstractExchange
- Rate limiting and error handling built-in
- Proxy support via environment variables

## Common Issues and Solutions

### Order Synchronization
- Orders may be out of sync between OctoBot and exchange
- Use `OrdersManager.update_order_from_exchange()` for manual sync
- Enable `enable_order_auto_synchronization` for automatic updates

### Portfolio Balance Issues
- Balance updates triggered by order fills
- Portfolio synchronization attempts limited by `MAX_PORTFOLIO_SYNC_ATTEMPTS`
- Use `await trader.refresh_portfolio()` to force refresh

### Exchange Connectivity
- Handle `UnreachableExchange` errors gracefully  
- Implement retry logic with exponential backoff
- Check `exchange.is_unreachable` before operations

## Environment Variables

Key configuration through environment variables:
- `CCXT_DEFAULT_CACHE_LIMIT`: CCXT cache size (default: 1000)
- `DEFAULT_REQUEST_TIMEOUT`: API request timeout (default: 20000ms)
- `ENABLE_CCXT_RATE_LIMIT`: Enable exchange rate limiting (default: True)
- `MAX_CANDLES_IN_RAM`: Max candles per manager (default: 3000)

## Dependencies

### Core Dependencies
- **ccxt**: Exchange connectivity (pinned to 4.5.0)
- **numpy**: Numerical operations (1.26.3)
- **OctoBot-Commons**: Shared utilities and enums
- **OctoBot-Backtesting**: Backtesting engine integration
- **trading-backend**: Backend trading services

### Development Dependencies
- **pytest**: Testing framework with async support
- **pylint**: Code linting (version < 2.15.2 due to bug)
- **coverage**: Test coverage reporting
- **mock**: Test mocking utilities
