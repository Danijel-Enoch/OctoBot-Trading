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
import octobot_trading.exchanges.types.websocket_exchange as websocket_exchange


class WeexWebSocketExchange(websocket_exchange.WebSocketExchange):
    """
    WEEX WebSocket Exchange implementation for OctoBot
    Provides real-time data streaming from WEEX exchange
    """

    # WebSocket configuration
    EXCHANGE_FEEDS = {
        trading_enums.WebsocketFeeds.TICKER: True,
        trading_enums.WebsocketFeeds.TRADES: True,
        trading_enums.WebsocketFeeds.L2_BOOK: True,
        trading_enums.WebsocketFeeds.CANDLE: True,
        trading_enums.WebsocketFeeds.ORDERS: True,
        trading_enums.WebsocketFeeds.PORTFOLIO: True,
        trading_enums.WebsocketFeeds.POSITION: False,  # Spot exchange, no positions
    }

    @classmethod
    def get_name(cls) -> str:
        return "weex"

    @classmethod
    def is_supporting_exchange(cls, exchange_candidate_name) -> bool:
        return cls.get_name() == exchange_candidate_name.lower()

    def get_websocket_endpoints(self) -> dict:
        """
        Return WEEX WebSocket endpoints
        """
        return {
            "public": "wss://ws-spot.weex.com/v2/ws/public",
            "private": "wss://ws-spot.weex.com/v2/ws/private"
        }

    def get_supported_websocket_feeds(self) -> dict:
        """
        Return supported WebSocket feeds for WEEX
        """
        return {
            # Market data feeds
            "ticker": {
                "channel_pattern": "ticker.{symbol}",
                "description": "24hr ticker statistics",
            },
            "depth": {
                "channel_pattern": "depth.{symbol}.{levels}",  # levels: 15 or 200
                "description": "Order book depth updates",
            },
            "trades": {
                "channel_pattern": "trades.{symbol}",
                "description": "Public trade executions",
            },
            "kline": {
                "channel_pattern": "kline.LAST_PRICE.{symbol}.{interval}",
                "description": "Candlestick/K-line updates",
            },
            # Private feeds (require authentication)
            "account": {
                "channel_pattern": "account",
                "description": "Account balance updates",
                "private": True,
            },
            "orders": {
                "channel_pattern": "orders",
                "description": "Order status updates",
                "private": True,
            },
            "fill": {
                "channel_pattern": "fill",
                "description": "Trade execution updates",
                "private": True,
            },
        }

    def get_websocket_intervals_mapping(self) -> dict:
        """
        Map OctoBot time frames to WEEX WebSocket intervals
        """
        return {
            "1m": "MINUTE_1",
            "5m": "MINUTE_5", 
            "15m": "MINUTE_15",
            "30m": "MINUTE_30",
            "1h": "HOUR_1",
            "2h": "HOUR_2",
            "4h": "HOUR_4",
            "6h": "HOUR_6",
            "8h": "HOUR_8",
            "12h": "HOUR_12",
            "1d": "DAY_1",
            "1w": "WEEK_1",
            "1M": "MONTH_1",
        }

    def get_ping_message(self) -> dict:
        """
        Return ping message format for WEEX WebSocket
        """
        return {"event": "pong", "time": None}  # time will be filled from server ping

    def get_pong_message(self, ping_data: dict) -> dict:
        """
        Return pong message in response to server ping
        """
        return {"event": "pong", "time": ping_data.get("time")}

    def get_subscribe_message(self, channel: str) -> dict:
        """
        Return subscription message format for WEEX WebSocket
        """
        return {
            "event": "subscribe",
            "channel": channel
        }

    def get_unsubscribe_message(self, channel: str) -> dict:
        """
        Return unsubscription message format for WEEX WebSocket
        """
        return {
            "event": "unsubscribe", 
            "channel": channel
        }

    def parse_websocket_symbol(self, symbol: str) -> str:
        """
        Convert OctoBot symbol format to WEEX WebSocket format
        WEEX uses symbols like BTCUSDT_SPBL for spot pairs
        """
        if not symbol.endswith("_SPBL"):
            return f"{symbol}_SPBL"
        return symbol

    def format_channel_name(self, feed_type: str, symbol: str = None, **kwargs) -> str:
        """
        Format channel name for WEEX WebSocket subscription
        """
        feeds_mapping = self.get_supported_websocket_feeds()
        
        if feed_type not in feeds_mapping:
            raise ValueError(f"Unsupported feed type: {feed_type}")
        
        channel_pattern = feeds_mapping[feed_type]["channel_pattern"]
        
        # Handle different feed types
        if feed_type == "ticker" and symbol:
            return channel_pattern.format(symbol=self.parse_websocket_symbol(symbol))
        
        elif feed_type == "depth" and symbol:
            levels = kwargs.get("levels", 15)  # Default to 15 levels
            return channel_pattern.format(
                symbol=self.parse_websocket_symbol(symbol), 
                levels=levels
            )
        
        elif feed_type == "trades" and symbol:
            return channel_pattern.format(symbol=self.parse_websocket_symbol(symbol))
        
        elif feed_type == "kline" and symbol:
            interval = kwargs.get("interval", "MINUTE_1")
            # Map OctoBot interval to WEEX format if needed
            interval_map = self.get_websocket_intervals_mapping()
            if interval in interval_map:
                interval = interval_map[interval]
            return channel_pattern.format(
                symbol=self.parse_websocket_symbol(symbol),
                interval=interval
            )
        
        elif feed_type in ["account", "orders", "fill"]:
            # Private channels don't require symbol
            return channel_pattern
        
        else:
            return channel_pattern

    def is_authenticated_channel(self, channel: str) -> bool:
        """
        Check if a channel requires authentication
        """
        private_channels = ["account", "orders", "fill"]
        return any(private_ch in channel for private_ch in private_channels)

    def get_authentication_headers(self) -> dict:
        """
        Return authentication headers for private WebSocket connections
        Based on WEEX API documentation
        """
        # This will be implemented by the connector with proper signature generation
        return {
            "ACCESS-KEY": "",
            "ACCESS-PASSPHRASE": "", 
            "ACCESS-TIMESTAMP": "",
            "ACCESS-SIGN": ""
        }

    def parse_websocket_message(self, message: dict) -> dict:
        """
        Parse incoming WebSocket message from WEEX
        """
        parsed = {
            "event_type": message.get("event"),
            "channel": message.get("channel"),
            "data": message.get("data"),
            "timestamp": message.get("timestamp"),
        }
        
        # Handle different message types
        if message.get("event") == "ping":
            parsed["message_type"] = "ping"
            parsed["ping_data"] = {"time": message.get("time")}
        
        elif message.get("event") == "subscribed":
            parsed["message_type"] = "subscription_ack"
        
        elif message.get("event") == "unsubscribed":
            parsed["message_type"] = "unsubscription_ack"
        
        elif message.get("event") == "payload":
            parsed["message_type"] = "data"
            
            # Parse different data types
            channel = message.get("channel", "")
            if "ticker" in channel:
                parsed["data_type"] = "ticker"
            elif "depth" in channel:
                parsed["data_type"] = "orderbook"
            elif "trades" in channel:
                parsed["data_type"] = "trades"
            elif "kline" in channel:
                parsed["data_type"] = "kline"
            elif channel == "account":
                parsed["data_type"] = "account"
            elif channel == "orders":
                parsed["data_type"] = "orders"
            elif channel == "fill":
                parsed["data_type"] = "fills"
        
        return parsed

    def get_max_connections(self) -> int:
        """
        Return maximum WebSocket connections allowed by WEEX
        """
        return 100  # 100 concurrent connections per IP

    def get_connection_limits(self) -> dict:
        """
        Return connection and subscription limits for WEEX WebSocket
        """
        return {
            "max_connections_per_ip": 100,
            "max_subscriptions_per_connection": 100,
            "operations_per_hour": 240,
            "connection_requests_per_5min": 300,
        }
