"""
    The orderupdate class is designed to facilitate asynchronous communication with the DhanHQ API via WebSocket.
    It enables users to subscribe to market data for a list of instruments and receive real-time updates.

    :copyright: (c) 2025 by Dhan.
    :license: see LICENSE for details.
"""

import asyncio
import websockets
import json
from typing import Callable, Optional


class OrderUpdate:
    """
    A class to manage WebSocket connections for order updates.

    Attributes:
        client_id (str): The client ID for authentication.
        access_token (str): The access token for authentication.
        order_feed_wss (str): The WebSocket URL for order updates.
    """

    on_update: Optional[Callable[[dict], None]] = None

    def __init__(self, dhan_context):
        """
        Initializes the OrderSocket with client ID and access token.

        Args:
            client_id (str): The client ID for authentication.
            access_token (str): The access token for authentication.
        """
        self.client_id = dhan_context.get_client_id()
        self.access_token = dhan_context.get_access_token()
        self.order_feed_wss = "wss://api-order-update.dhan.co"

    async def connect_order_update(self):
        """
        Connects to the WebSocket and listens for order updates.

        This method authenticates the client and processes incoming messages.
        """
        async with websockets.connect(self.order_feed_wss) as websocket:
            auth_message = {
                "LoginReq": {
                    "MsgCode": 42,
                    "ClientId": str(self.client_id),
                    "Token": str(self.access_token)
                },
                "UserType": "SELF"
            }

            await websocket.send(json.dumps(auth_message))
            print(f"Sent subscribe message: {auth_message}")

            async for message in websocket:
                data = json.loads(message)
                self.handle_order_update(data)

    def handle_order_update(self, order_update):
        """
        Handles incoming order update messages.

        Args:
            order_update (dict): The order update message received from the WebSocket.
        """
        if order_update.get('Type') == 'order_alert':
            if self.on_update and callable(self.on_update):
                return self.on_update(order_update)

            data = order_update.get('Data', {})
            if "orderNo" in data:
                order_id = data["orderNo"]
                status = data.get("status", "Unknown status")
                print(f"Status: {status}, Order ID: {order_id}, Data: {data}")
            else:
                print(f"Order Update received: {data}")
        else:
            print(f"Unknown message received: {order_update}")

    def connect_to_dhan_websocket_sync(self):
        """
        Synchronously connects to the WebSocket.

        This method runs the asynchronous connect_order_update method in a new event loop.
        """
        try:
            return self.connect_order_update()
        except Exception as e:
            print(f"Error in connect_to_dhan_websocket: {e}")
