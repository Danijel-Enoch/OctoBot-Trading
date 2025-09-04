#  Drakkar-Software OctoBot-Trading
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.

import octobot_trading.enums as trading_enums
import octobot_trading.exchanges.types.rest_exchange as rest_exchange


class WeexExchange(rest_exchange.RestExchange):
    """
    WEEX (WXT) Exchange implementation for OctoBot
    Provides integration with WEEX's spot trading APIs
    """

    # Exchange configuration
    FIX_MARKET_STATUS = True
    SUPPORTS_SET_MARGIN_TYPE = False  # Spot exchange only
    ENABLE_SPOT_BUY_MARKET_WITH_COST = True
    
    # Exchange specific error patterns
    EXCHANGE_ORDER_NOT_FOUND_ERRORS = [
        ["FAILED_ORDER_NOT_FOUND"],
        ["Order does not exist"],
    ]
    
    EXCHANGE_PERMISSION_ERRORS = [
        ["Invalid permissions"],
        ["Invalid API Key"],
        ["Incorrect API key/Passphrase"],
    ]
    
    EXCHANGE_AUTHENTICATION_ERRORS = [
        ["API verification failed"],
        ["Header \"ACCESS_KEY\" is required"],
        ["Header \"ACCESS_SIGN\" is required"],
        ["Header \"ACCESS_PASSPHRASE\" is required"],
        ["Request timestamp expired"],
    ]
    
    EXCHANGE_MISSING_FUNDS_ERRORS = [
        ["Account balance is insufficient"],
        ["Insufficient balance"],
    ]
    
    EXCHANGE_ORDER_UNCANCELLABLE_ERRORS = [
        ["Order cannot be cancelled"],
        ["Order is already filled"],
        ["Order is already cancelled"],
    ]

    @classmethod
    def get_name(cls) -> str:
        return "weex"

    @classmethod
    def is_supporting_exchange(cls, exchange_candidate_name) -> bool:
        return cls.get_name() == exchange_candidate_name.lower()

    @classmethod
    def get_supported_exchange_types(cls) -> list:
        """
        WEEX supports spot trading primarily
        """
        return [trading_enums.ExchangeTypes.SPOT]

    async def switch_to_account(self, account_type: trading_enums.AccountTypes):
        """
        WEEX uses different account types: SPOT, SPOT_V2, FUND, etc.
        This method handles account switching if needed
        """
        # For now, we'll primarily use SPOT account type
        # This can be extended in the future for other account types
        if account_type == trading_enums.AccountTypes.CASH:
            # Use spot account
            pass
        elif account_type == trading_enums.AccountTypes.MARGIN:
            # WEEX doesn't support margin trading in the same way
            raise NotImplementedError("Margin trading not yet supported on WEEX")
        elif account_type == trading_enums.AccountTypes.FUTURE:
            # WEEX has separate futures contracts
            raise NotImplementedError("Futures trading should use separate WEEX futures implementation")

    def get_additional_connector_config(self):
        """
        Additional configuration for WEEX connector
        """
        return {
            "spot_api_url": "https://api-spot.weex.com",
            "contract_api_url": "https://api-contract.weex.com",
            "websocket_public_url": "wss://ws-spot.weex.com/v2/ws/public",
            "websocket_private_url": "wss://ws-spot.weex.com/v2/ws/private",
            "rate_limit": 20,  # 20 requests/second for public endpoints
            "private_rate_limit": 10,  # 10 requests/second for private endpoints
            "supported_symbols_suffix": "_SPBL",  # WEEX uses _SPBL suffix for spot pairs
        }

    def get_market_status_additional_fix_values(self, symbol, market_status, price_example=None):
        """
        Apply WEEX specific market status fixes
        """
        # WEEX uses specific precision and lot size formats
        if market_status:
            # Ensure step size is properly formatted
            if "stepSize" in market_status.get("info", {}):
                step_size = market_status["info"]["stepSize"]
                if step_size and float(step_size) > 0:
                    market_status["precision"]["amount"] = self._get_precision_from_step_size(step_size)
            
            # Ensure tick size is properly formatted
            if "tickSize" in market_status.get("info", {}):
                tick_size = market_status["info"]["tickSize"]
                if tick_size and float(tick_size) > 0:
                    market_status["precision"]["price"] = self._get_precision_from_step_size(tick_size)
        
        return market_status

    def _get_precision_from_step_size(self, step_size_str):
        """
        Convert step size string to precision (number of decimal places)
        """
        try:
            step_size = float(step_size_str)
            if step_size >= 1:
                return 0
            
            # Count decimal places
            decimal_str = f"{step_size:.10f}".rstrip('0')
            if '.' in decimal_str:
                return len(decimal_str.split('.')[1])
            return 0
        except (ValueError, TypeError):
            return 8  # Default precision

    def get_order_additional_params(self, order) -> dict:
        """
        Get additional parameters for WEEX order creation
        """
        params = {}
        
        # Add client order ID for tracking
        if hasattr(order, 'order_id') and order.order_id:
            params['clientOrderId'] = str(order.order_id)
        
        # Set force parameter based on order type
        if hasattr(order, 'order_type'):
            if order.order_type in [trading_enums.TraderOrderType.STOP_LOSS, trading_enums.TraderOrderType.TAKE_PROFIT]:
                params['force'] = 'normal'
            elif order.order_type in [trading_enums.TraderOrderType.BUY_LIMIT, trading_enums.TraderOrderType.SELL_LIMIT]:
                params['force'] = 'normal'  # Can be changed to 'postOnly', 'fok', 'ioc' as needed
        
        return params

    def get_supported_time_frames(self) -> list:
        """
        Return supported time frames for WEEX
        Based on the API documentation: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 1w, 1M
        """
        return [
            "1m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "1w", "1M"
        ]

    @classmethod
    def get_default_balance(cls):
        """
        Return default balance structure for WEEX
        """
        return {
            "info": {},
            "datetime": None,
            "timestamp": None,
            "total": {},
            "free": {},
            "used": {}
        }

    def parse_account_type(self, raw_account_type: str) -> trading_enums.AccountTypes:
        """
        Parse WEEX account type to OctoBot enum
        """
        account_type_map = {
            "EXCHANGE": trading_enums.AccountTypes.CASH,
            "SPOT": trading_enums.AccountTypes.CASH,
            "SPOT_V2": trading_enums.AccountTypes.CASH,
            "FUND": trading_enums.AccountTypes.CASH,
            "CONTRACT": trading_enums.AccountTypes.FUTURE,
            "USD_MIX": trading_enums.AccountTypes.FUTURE,
            "USDT_MIX": trading_enums.AccountTypes.FUTURE,
            "OTC_SGD": trading_enums.AccountTypes.CASH,
        }
        return account_type_map.get(raw_account_type.upper(), trading_enums.AccountTypes.CASH)

    def get_max_orders_count(self, symbol: str, order_type: trading_enums.TraderOrderType) -> int:
        """
        Get maximum orders count for WEEX
        WEEX supports batch orders up to 50 orders per request
        """
        return 50  # Based on batch order limit from API docs
