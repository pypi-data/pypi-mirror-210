from typing import Any, Dict, Optional
from unittest import TestCase, main

import mock
import pytest
from fastapi import HTTPException
from mock import Mock
from sag_py_auth.models import Token

from sag_py_auth_brand.brand_jwt_auth import BrandJwtAuth
from sag_py_auth_brand.constants import LogMessages

from .helpers import build_sample_jwt_auth, get_token


class TestVerifyBrandAlias(TestCase):
    @mock.patch("sag_py_auth_brand.brand_jwt_auth.set_request_brand_alias_to_context")
    @mock.patch("sag_py_auth_brand.brand_jwt_auth.set_request_brand_to_context")
    def test__verify_brand__where_user_has_brand_alias(
        self, mock_set_brand_to_context: Mock, mock_set_brand_alias_to_context: Mock
    ) -> None:
        # Arrange
        brand_jwt_auth: BrandJwtAuth = build_sample_jwt_auth(["myEndpoint"])

        resource_access: Optional[Dict[str, Any]] = {
            "role-brand": {"roles": ["mybrandone"]},
            "role-brand-alias": {"roles": ["mybrandone", "firstalias", "secondalias"]},
        }

        token: Token = get_token(None, resource_access)

        # Act
        try:
            brand_jwt_auth._verify_brand(token, "secondalias")
        except Exception:
            pytest.fail("No exception expected if the brand is present in the token")

        # Assert

        # Has to be the brand of the request
        mock_set_brand_to_context.assert_called_once_with("secondalias")
        # Has to be the alias of the brand from the request.
        # The alias is the brand that has originally had access to the api
        # It is used in the entire background logic as brand
        # Note: Here we always get the brand that is present in both lists, role-brand and role-brand-aliases
        mock_set_brand_alias_to_context.assert_called_once_with("mybrandone")

    @mock.patch("sag_py_auth_brand.brand_jwt_auth.set_request_brand_alias_to_context")
    @mock.patch("sag_py_auth_brand.brand_jwt_auth.set_request_brand_to_context")
    def test__verify_brand__where_user_has_brand_alias_at_any_position(
        self, mock_set_brand_to_context: Mock, mock_set_brand_alias_to_context: Mock
    ) -> None:
        # Arrange
        brand_jwt_auth: BrandJwtAuth = build_sample_jwt_auth(["myEndpoint"])

        resource_access: Optional[Dict[str, Any]] = {
            "role-brand": {"roles": ["a-random-brand", "another-random-brand", "a-matching-alias"]},
            "role-brand-alias": {
                "roles": ["a-random-alias", "a-matching-alias", "another-random-alias", "the-request-alias"]
            },
        }

        token: Token = get_token(None, resource_access)

        # Act
        brand_jwt_auth._verify_brand(token, "the-request-alias")

        # Assert

        # Has to be the brand of the request
        mock_set_brand_to_context.assert_called_once_with("the-request-alias")

        # Has to be the alias of the brand from the request.
        # The alias is the brand that has originally had access to the api
        # It is used in the entire background logic as brand
        # Note: Here we always get the brand that is present in both lists, role-brand and role-brand-aliases
        mock_set_brand_alias_to_context.assert_called_once_with("a-matching-alias")

    @mock.patch("sag_py_auth_brand.brand_jwt_auth.set_request_brand_alias_to_context")
    @mock.patch("sag_py_auth_brand.brand_jwt_auth.set_request_brand_to_context")
    def test__verify_brand__with_missing_brand_alias(
        self, mock_set_brand_to_context: Mock, mock_set_brand_alias_to_context: Mock
    ) -> None:
        # Arrange
        brand_jwt_auth: BrandJwtAuth = build_sample_jwt_auth(["myEndpoint"])

        resource_access: Optional[Dict[str, Any]] = {
            "role-brand": {"roles": ["mybrandone"]},
            "role-brand-alias": {"roles": []},
        }

        token: Token = get_token(None, resource_access)

        # Act
        with pytest.raises(HTTPException) as exception, self.assertLogs(level="DEBUG") as log_watcher:
            brand_jwt_auth._verify_brand(token, "secondalias")

        self.assertTrue(LogMessages.MISSING_BRAND_ALIAS in "".join(log_watcher.output))
        assert exception.value.status_code == 403
        assert exception.value.detail == "Missing brand."
        mock_set_brand_to_context.assert_called_once_with(None)
        mock_set_brand_alias_to_context.assert_called_once_with(None)

    @mock.patch("sag_py_auth_brand.brand_jwt_auth.set_request_brand_alias_to_context")
    @mock.patch("sag_py_auth_brand.brand_jwt_auth.set_request_brand_to_context")
    def test__verify_brand__where_brand_aliases_is_missing_role_brand(
        self, mock_set_brand_to_context: Mock, mock_set_brand_alias_to_context: Mock
    ) -> None:
        # Arrange
        brand_jwt_auth: BrandJwtAuth = build_sample_jwt_auth(["myEndpoint"])

        resource_access: Optional[Dict[str, Any]] = {
            "role-brand": {"roles": ["mybrandone"]},
            "role-brand-alias": {"roles": ["firstalias", "secondalias"]},
        }

        token: Token = get_token(None, resource_access)

        # Act
        with pytest.raises(HTTPException) as exception, self.assertLogs(level="DEBUG") as log_watcher:
            brand_jwt_auth._verify_brand(token, "secondalias")

        self.assertTrue(LogMessages.MISSING_COMPOUND_BRAND in "".join(log_watcher.output))
        assert exception.value.status_code == 403
        assert exception.value.detail == "Missing brand."
        mock_set_brand_to_context.assert_called_once_with(None)
        mock_set_brand_alias_to_context.assert_called_once_with(None)

    @mock.patch("sag_py_auth_brand.brand_jwt_auth.set_request_brand_alias_to_context")
    @mock.patch("sag_py_auth_brand.brand_jwt_auth.set_request_brand_to_context")
    def test__verify_brand__where_brand_aliases_have_multiple_role_brands(
        self, mock_set_brand_to_context: Mock, mock_set_brand_alias_to_context: Mock
    ) -> None:
        # Arrange
        brand_jwt_auth: BrandJwtAuth = build_sample_jwt_auth(["myEndpoint"])

        resource_access: Optional[Dict[str, Any]] = {
            "role-brand": {"roles": ["mybrandone", "mybrandtwo"]},
            "role-brand-alias": {"roles": ["mybrandone", "mybrandtwo", "firstalias", "secondalias"]},
        }

        token: Token = get_token(None, resource_access)

        # Act
        with pytest.raises(HTTPException) as exception, self.assertLogs() as log_watcher:
            brand_jwt_auth._verify_brand(token, "secondalias")

        # Assert
        self.assertTrue(LogMessages.UNAMBIGUOUS_BRAND_ALIAS in "".join(log_watcher.output))
        assert exception.value.status_code == 403
        assert exception.value.detail == "Missing brand."
        mock_set_brand_to_context.assert_called_once_with(None)
        mock_set_brand_alias_to_context.assert_called_once_with(None)


if __name__ == "__main__":
    main()
