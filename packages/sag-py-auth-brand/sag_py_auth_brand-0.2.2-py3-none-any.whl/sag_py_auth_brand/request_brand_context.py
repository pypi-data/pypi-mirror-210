from contextvars import ContextVar
from typing import Optional

_request_brand: ContextVar[Optional[str]] = ContextVar("request_brand", default=None)
_request_brand_alias: ContextVar[Optional[str]] = ContextVar("request_brand_alias", default=None)


def get_brand() -> str:
    """Gets the context local brand. This is the brand for backend logic.
    It contains the compound brand alias if set and otherwise the request brand.
    See library contextvars for details.

    Returns: The brand
    """
    return get_request_brand_alias() or get_request_brand()


def get_request_brand() -> str:
    """Gets the context local brand. This is always the brand of the request.
    See library contextvars for details.

    Returns: The brand
    """
    current_brand: Optional[str] = _request_brand.get("")
    return current_brand or ""


def get_request_brand_alias() -> str:
    """Gets the context local brand alias. This is the brand used for backend logic if aliasing is used.
    See library contextvars for details.

    Returns: The brand alias
    """
    current_brand_alias: Optional[str] = _request_brand_alias.get("")
    return current_brand_alias or ""


def set_request_brand(brand_to_set: Optional[str]) -> None:
    """Sets the context local brand. This is always the brand of the request.
    See library contextvars for details."""
    _request_brand.set(brand_to_set)


def set_request_brand_alias(brand_alias_to_set: Optional[str]) -> None:
    """Sets the context local brand alias. This is the brand used for backend logic if it is set.
    See library contextvars for details."""
    _request_brand_alias.set(brand_alias_to_set)
