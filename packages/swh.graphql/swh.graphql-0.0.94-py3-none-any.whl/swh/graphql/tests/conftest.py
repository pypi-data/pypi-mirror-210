# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
from typing import Any, Optional

import pytest
from starlette.authentication import AuthCredentials, AuthenticationError, SimpleUser
from starlette.testclient import TestClient

from swh.auth.starlette.backends import BearerTokenAuthBackend
from swh.graphql import server as app_server

from .data import populate_dummy_data, populate_search_data


def mock_async(return_value: Any = None, error: Optional[Exception] = None):
    # FIXME, mock function for async. Can be removed on Python.3.8+
    async def func(*args, **kw):
        if error:
            raise error
        return return_value

    return func


@pytest.fixture(scope="session")
def test_app():
    os.environ["SWH_CONFIG_FILENAME"] = os.path.join(
        os.path.dirname(__file__), "../config/test.yml"
    )
    app = app_server.make_app_from_configfile()
    return app


@pytest.fixture(autouse=True)
def authenticated_user(mocker):
    return_value = AuthCredentials(["Authenticated"]), SimpleUser("user")
    mocker.patch.object(
        BearerTokenAuthBackend,
        "authenticate",
        side_effect=mock_async(return_value=return_value),
    )


@pytest.fixture
def anonymous_user(mocker):
    mocker.patch.object(
        BearerTokenAuthBackend,
        "authenticate",
        side_effect=mock_async(return_value=None),
    )


@pytest.fixture
def authentication_error(mocker):
    mocker.patch.object(
        BearerTokenAuthBackend,
        "authenticate",
        side_effect=mock_async(error=AuthenticationError("auth error")),
    )


@pytest.fixture(scope="session")
def storage(test_app):
    storage = app_server.get_storage()
    # populate the in-memory storage
    populate_dummy_data(storage)
    return storage


@pytest.fixture(scope="session")
def search(test_app):
    search = app_server.get_search()
    search.initialize()
    # populate the in-memory search
    populate_search_data(search)
    return search


@pytest.fixture(scope="session")
def client(test_app, storage, search):
    yield TestClient(test_app)


@pytest.fixture
def high_query_cost():
    query_cost = app_server.graphql_cfg["max_query_cost"]["user"]
    app_server.graphql_cfg["max_query_cost"]["user"] = 2000
    yield
    app_server.graphql_cfg["max_query_cost"]["user"] = query_cost


@pytest.fixture
def none_query_cost():
    # There will not be any query cost limit in this case
    query_cost = app_server.graphql_cfg["max_query_cost"]["user"]
    app_server.graphql_cfg["max_query_cost"]["user"] = None
    yield
    app_server.graphql_cfg["max_query_cost"]["user"] = query_cost
