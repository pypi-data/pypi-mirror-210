import datetime
import enum
import functools
import json
from typing import Any, Dict, Optional

from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, Scope
from strawberry.schema import BaseSchema

from strawberry_django_pubsub.context import StrawberryDjangoWsContext
from strawberry_django_pubsub.debug import pretty_print_event
from strawberry_django_pubsub.exceptions import (
    WebSocketAcceptConnection,
    WebSocketDenyConnection,
)
from strawberry_django_pubsub.handlers.graphql_transport_ws_handler import (
    GraphQLTransportWSHandler,
)
from strawberry_django_pubsub.utils import get_handler_name


class WebSocketState(enum.Enum):
    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2


__all__ = ["DjangoWsGraphQL"]


WEBSOCKET_TYPE = "websocket"


class DjangoWsGraphQL:
    def __init__(self, schema: BaseSchema, debug: bool = False, *args, **kwargs):
        self.schema = schema
        self.debug = debug

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        """
        Handles ASGI Websocket protocol for Django, without channels dependency.
        """

        self.scope = scope
        self._send = send

        self.client_state = WebSocketState.CONNECTING
        self.application_state = WebSocketState.CONNECTING

        # ensure where mounted on a websocket
        if not self.scope["type"] == WEBSOCKET_TYPE:
            pretty_print_event(
                "Connection denied", context=self.scope, debug=self.debug
            )
            raise WebSocketDenyConnection()

        # dispatch websocket protocol
        while True:
            message = await receive()
            await self.dispatch(message)

    async def dispatch(self, message):
        """
        Works out what to do with a message.
        """

        pretty_print_event("dispatch", context=message, debug=self.debug)

        handler = getattr(self, get_handler_name(message), None)
        if handler:
            await handler(message)

    async def websocket_connect(self, *args):
        """
        Called when a WebSocket connection is opened.
        """
        try:
            await self.connect()
        except WebSocketAcceptConnection:
            await self.accept()
        except WebSocketDenyConnection:
            await self.close()

    async def send(self, message, close=False):
        """
        send data
        """
        await self._send(message)

    async def get_context(
        self,
        request: Optional["DjangoWsGraphQL"] = None,
        connection_params: Optional[Dict[str, Any]] = None,
    ) -> StrawberryDjangoWsContext:
        return StrawberryDjangoWsContext(
            request=request, connection_params=connection_params
        )

    @property
    def headers(self) -> Dict[str, str]:
        return {
            header_name.decode().lower(): header_value.decode()
            for header_name, header_value in self.scope["headers"]
        }

    async def get_root_value(self, request: Optional["DjangoWsGraphQL"] = None) -> Any:
        return None

    async def accept(self, subprotocol=None):
        """
        Accepts an incoming socket
        """

        await self.send({"type": "websocket.accept", "subprotocol": subprotocol})

    async def connect(self) -> None:
        self._handler = GraphQLTransportWSHandler(
            schema=self.schema,
            debug=True,
            connection_init_wait_timeout=datetime.timedelta(minutes=1),
            get_context=self.get_context,
            get_root_value=self.get_root_value,
            ws=self,
        )

        await self._handler.handle()
        return None

    async def websocket_receive(self, message):
        """
        Called when a WebSocket frame is received. Decodes it and passes it
        to receive().
        """
        if "text" in message:
            await self.receive(text_data=message["text"])
        else:
            await self.receive(bytes_data=message["bytes"])

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data:
            await self.receive_json(await self.decode_json(text_data), **kwargs)
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    async def receive_json(self, content, **kwargs):
        await self._handler.handle_message(content)

    async def send_json(self, content, close=False) -> None:
        """
        Encode the given content as JSON and send it to the client.
        """
        pretty_print_event("send_json", context=content, debug=self.debug)

        await self.send(
            {"type": "websocket.send", "text": await self.encode_json(content)},
            close=close,
        )

    async def disconnect(self, code) -> None:
        await self._handler.handle_disconnect(code)

    @classmethod
    async def decode_json(cls, text_data):
        return json.loads(text_data)

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content)

    @classmethod
    def as_asgi(cls, **initkwargs):
        """
        Return an ASGI v3 single callable that instantiates a consumer instance
        per scope. Similar in purpose to Django's as_view().

        initkwargs will be used to instantiate the consumer instance.
        """

        async def app(
            scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
        ):
            consumer = cls(**initkwargs)
            return await consumer(scope, receive, send)

        app.consumer_class = cls
        app.consumer_initkwargs = initkwargs

        # take name and docstring from class
        functools.update_wrapper(app, cls, updated=())
        return app
