from logging import LogRecord
from typing import cast

from sag_py_auth_brand.models import BrandLogRecord
from sag_py_auth_brand.request_brand_context import set_request_brand as set_request_brand_to_context
from sag_py_auth_brand.request_brand_context import set_request_brand_alias as set_request_brand_alias_to_context
from sag_py_auth_brand.request_brand_logging_filter import RequestBrandLoggingFilter


def test__get_field_value__with_brand() -> None:
    # Arrange
    logging_filter = RequestBrandLoggingFilter()
    log_entry = LogRecord("LogRecord", 0, "path.py", 100, "A test message", None, None)

    set_request_brand_to_context("myBrand")
    set_request_brand_alias_to_context(None)

    # Act
    logging_filter.filter(log_entry)

    # Assert
    assert log_entry.msg == "A test message"
    assert cast(BrandLogRecord, log_entry).request_brand == "myBrand"
    assert cast(BrandLogRecord, log_entry).brand == "myBrand"


def test__get_field_value__with_brand_alias() -> None:
    # Arrange
    logging_filter = RequestBrandLoggingFilter()
    log_entry = LogRecord("LogRecord", 0, "path.py", 100, "A test message", None, None)

    set_request_brand_to_context(None)
    set_request_brand_alias_to_context("myBrandAlias")

    # Act
    logging_filter.filter(log_entry)

    # Assert
    assert log_entry.msg == "A test message"
    assert not hasattr(log_entry, "request_brand")
    assert cast(BrandLogRecord, log_entry).request_brand_alias == "myBrandAlias"
    assert cast(BrandLogRecord, log_entry).brand == "myBrandAlias"


def test__get_field_value__without_data() -> None:
    # Arrange
    logging_filter = RequestBrandLoggingFilter()
    log_entry = LogRecord("LogRecord", 0, "path.py", 100, "A test message", None, None)

    set_request_brand_to_context(None)
    set_request_brand_alias_to_context(None)

    # Act
    logging_filter.filter(log_entry)

    # Assert
    assert log_entry.msg == "A test message"
    assert not hasattr(log_entry, "request_brand")
    assert not hasattr(log_entry, "request_brand_alias")
    assert not hasattr(log_entry, "brand")


def test__get_field_value__with_both() -> None:
    # Arrange
    logging_filter = RequestBrandLoggingFilter()
    log_entry = LogRecord("LogRecord", 0, "path.py", 100, "A test message", None, None)

    set_request_brand_to_context("myBrand")
    set_request_brand_alias_to_context("myBrandAlias")

    # Act
    logging_filter.filter(log_entry)

    # Assert
    assert log_entry.msg == "A test message"
    assert cast(BrandLogRecord, log_entry).request_brand == "myBrand"
    assert cast(BrandLogRecord, log_entry).request_brand_alias == "myBrandAlias"
    assert cast(BrandLogRecord, log_entry).brand == "myBrandAlias"
