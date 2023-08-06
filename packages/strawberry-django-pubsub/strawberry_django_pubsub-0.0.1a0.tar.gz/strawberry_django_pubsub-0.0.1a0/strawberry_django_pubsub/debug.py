import datetime
import json
from json import JSONEncoder
from typing import Any, Dict, Optional, Union


class DebugJSONEncoder(JSONEncoder):
    """
    Custom JSONEncoder to handle debug output
    """

    def default(self, o: Any) -> Any:
        return repr(o)


def pretty_print_event(
    event: Optional[str],
    context: Union[str, Dict["str", Any]],
    variables: Optional[Dict["str", Any]] = None,
    debug: bool = False,
) -> None:
    """
    Pretty print a Websocket operation using pygments.

    """

    if not debug:
        return

    try:
        from pygments import highlight, lexers
        from pygments.formatters import Terminal256Formatter
    except ImportError as e:
        raise ImportError(
            "pygments is not installed but is required for debug output, install it "
            "directly or run `pip install strawberry-graphql[debug-server]`"
        ) from e

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{now}]: {event or 'No event name'}")  # noqa: T201
    context_json = json.dumps(context, indent=4, cls=DebugJSONEncoder)
    print(
        highlight(context_json, lexers.JsonLexer(), Terminal256Formatter())
    )  # noqa: T201

    if variables:
        variables_json = json.dumps(variables, indent=4, cls=DebugJSONEncoder)

        print(  # noqa: T201
            highlight(variables_json, lexers.JsonLexer(), Terminal256Formatter())
        )
