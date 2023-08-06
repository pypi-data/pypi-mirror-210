from sag_py_auth_brand.request_brand_context import get_brand as get_brand_from_context
from sag_py_auth_brand.request_brand_context import get_request_brand as get_request_brand_from_context
from sag_py_auth_brand.request_brand_context import get_request_brand_alias as get_request_brand_alias_from_context
from sag_py_auth_brand.request_brand_context import set_request_brand as set_request_brand_to_context
from sag_py_auth_brand.request_brand_context import set_request_brand_alias as set_request_brand_alias_to_context


def test__get_brand__not_set() -> None:
    # Arrange
    set_request_brand_to_context(None)
    set_request_brand_alias_to_context(None)

    # Act
    actual_request_brand: str = get_request_brand_from_context()
    actual_request_brand_alias: str = get_request_brand_alias_from_context()
    actual_brand: str = get_brand_from_context()

    assert not actual_request_brand
    assert not actual_request_brand_alias
    assert not actual_brand


def test__get_brand__with_previously_set_brand() -> None:
    # Arrange
    set_request_brand_to_context("myBrand")
    set_request_brand_alias_to_context(None)

    # Act
    actual_request_brand: str = get_request_brand_from_context()
    actual_request_brand_alias: str = get_request_brand_alias_from_context()
    actual_brand: str = get_brand_from_context()

    assert actual_request_brand == "myBrand"
    assert not actual_request_brand_alias
    assert actual_brand == "myBrand"


def test__get_brand__with_previously_set_brand_alias() -> None:
    # Arrange
    set_request_brand_to_context(None)
    set_request_brand_alias_to_context("myBrandAlias")

    # Act
    actual_request_brand: str = get_request_brand_from_context()
    actual_request_brand_alias: str = get_request_brand_alias_from_context()
    actual_brand: str = get_brand_from_context()

    assert not actual_request_brand
    assert actual_request_brand_alias == "myBrandAlias"
    assert actual_brand == "myBrandAlias"


def test__get_brand__with_previously_set_both() -> None:
    # Arrange
    set_request_brand_to_context("myBrand")
    set_request_brand_alias_to_context("myBrandAlias")

    # Act
    actual_request_brand: str = get_request_brand_from_context()
    actual_request_brand_alias: str = get_request_brand_alias_from_context()
    actual_brand: str = get_brand_from_context()

    # Assert
    assert actual_request_brand == "myBrand"
    assert actual_request_brand_alias == "myBrandAlias"
    assert actual_brand == "myBrandAlias"
