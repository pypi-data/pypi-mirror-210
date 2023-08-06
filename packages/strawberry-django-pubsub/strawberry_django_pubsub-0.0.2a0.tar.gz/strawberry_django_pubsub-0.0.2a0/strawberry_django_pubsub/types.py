import asyncio
from typing import Dict, MutableSet

from strawberry_django_pubsub.event import Event

PublisherQueue = asyncio.Queue[Event]
SubscriberQueue = asyncio.Queue[Event]

Subscribed = MutableSet[str]
Subscriptions = Dict[str, MutableSet[SubscriberQueue]]
