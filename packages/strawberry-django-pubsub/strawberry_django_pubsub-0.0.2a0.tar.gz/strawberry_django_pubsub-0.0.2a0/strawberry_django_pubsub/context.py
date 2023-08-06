from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from strawberry_django_pubsub.asgi import DjangoWsGraphQL


@dataclass
class StrawberryDjangoWsContext:
    """
    A StrawberryDjangoWsContext context
    """

    request: "DjangoWsGraphQL"
    connection_params: Optional[Dict[str, Any]] = None

    @property
    def ws(self) -> "DjangoWsGraphQL":
        return self.request

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)
