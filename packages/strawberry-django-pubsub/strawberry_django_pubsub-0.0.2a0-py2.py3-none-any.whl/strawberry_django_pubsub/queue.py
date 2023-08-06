import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, AsyncIterator, Optional

from strawberry_django_pubsub.event import Event
from strawberry_django_pubsub.types import (
    PublisherQueue,
    Subscribed,
    SubscriberQueue,
    Subscriptions,
)


class Unsubscribed(Exception):
    pass


class PubSubQueue:
    def __init__(self):
        self._subscribed: Subscribed = set()

    async def connect(self) -> None:
        """
        Connect handler, it will invoke it's publish queue
        """
        self._published: PublisherQueue = asyncio.Queue()

    async def subscribe(self, channel: str) -> None:
        """
        subscribe to a channel
        """
        self._subscribed.add(channel)

    async def unsubscribe(self, channel: str) -> None:
        """
        unsubscribe from a channel
        """
        self._subscribed.remove(channel)

    async def publish(self, channel: str, payload: Any) -> None:
        """
        publish event on published queue
        """
        event = Event(channel=channel, payload=payload)
        await self._published.put(event)

    async def next_published(self) -> Event:
        """
        iterate published queue and pop off events
        """
        while True:
            event = await self._published.get()
            if event.channel in self._subscribed:
                return event


class QueueBroadcast:
    def __init__(self):
        self._subscribers: Subscriptions = {}
        self._queue: PubSubQueue = PubSubQueue()

    async def __aenter__(self) -> "QueueBroadcast":
        await self.connect()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        """
        connect method: setup queue and run a seperate listener task
        """
        await self._queue.connect()
        self._current_task = asyncio.create_task(self._listener())

    async def disconnect(self) -> None:
        """
        disconnect method: we cleanup all running tasks.
        rather then calling this method directly it should
        be mounted on a shutdown of lifespan queue.
        """

        if self._current_task.done():
            self._current_task.result()
        else:
            self._current_task.cancel()

    async def _listener(self) -> None:
        while True:
            event = await self._queue.next_published()
            for queue in list(self._subscribers.get(event.channel, [])):
                await queue.put(event)

    async def publish(self, channel: str, payload: Any) -> None:
        await self._queue.publish(channel, payload)

    @asynccontextmanager
    async def subscribe(self, channel: str) -> AsyncIterator["Subscriber"]:
        """
        subscribe to channel and start listening for events on from SubscriberQueue
        """

        queue: SubscriberQueue = asyncio.Queue()

        try:
            if not self._subscribers.get(channel):
                await self._queue.subscribe(channel)
                self._subscribers[channel] = set([queue])
            else:
                self._subscribers[channel].add(queue)

            yield Subscriber(queue)

            self._subscribers[channel].remove(queue)
            if not self._subscribers.get(channel):
                del self._subscribers[channel]
                await self._queue.unsubscribe(channel)
        finally:
            await queue.put(None)


class Subscriber:
    def __init__(self, queue: SubscriberQueue) -> None:
        self._queue = queue

    async def __aiter__(self) -> Optional[AsyncGenerator]:
        """
        generator to fetch Event, this methods keeps on listening
        until it's queue is empty.
        """
        try:
            while True:
                yield await self.get()
        except Unsubscribed:
            pass

    async def get(self) -> Event:
        """
        get events from pubsub broadcaster
        """
        event = await self._queue.get()
        if event is None:
            raise Unsubscribed()
        return event


queue = QueueBroadcast()
