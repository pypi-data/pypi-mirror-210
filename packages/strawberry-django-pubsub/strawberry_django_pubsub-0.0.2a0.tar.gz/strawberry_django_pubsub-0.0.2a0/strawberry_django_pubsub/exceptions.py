from typing import Optional


class WebSocketAcceptConnection(Exception):
    """
    Raised during a websocket.connect (or other supported connection) handler
    to accept the connection.
    """

    pass


class WebSocketDenyConnection(Exception):
    """
    Raised during a websocket.connect (or other supported connection) handler
    to deny the connection.
    """

    pass


class WebSocketConnectionDisconnect(Exception):
    """
    Raised when connection is dropped; this exception should only be called
    explicit in debug mode only.
    """

    def __init__(self, code: int = 1000, reason: Optional[str] = None) -> None:
        self.code = code
        self.reason = reason or ""
