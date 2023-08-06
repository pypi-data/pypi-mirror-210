"""
Pure zero-dependency JSON-RPC 2.0 implementation.
"""

from typing import Final

from .asgi import ASGIHandler
from .dispatcher import AsyncDispatcher
from .errors import Error, ErrorEnum
from .request import BatchRequest, Request
from .response import BatchResponse, Response
from .serializer import JSONSerializer

__all__: Final[tuple[str, ...]] = (
    "ASGIHandler",
    "AsyncDispatcher",
    "BatchRequest",
    "BatchResponse",
    "Error",
    "ErrorEnum",
    "JSONSerializer",
    "Request",
    "Response",
)
