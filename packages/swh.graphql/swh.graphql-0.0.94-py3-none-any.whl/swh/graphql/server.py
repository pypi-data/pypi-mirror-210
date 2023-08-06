# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
from typing import Any, Dict, Optional

from aiocache import Cache
from ariadne.asgi import GraphQL
from starlette.applications import Starlette
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    UnauthenticatedUser,
)
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route

from swh.auth.starlette.backends import BearerTokenAuthBackend
from swh.core import config
from swh.search import get_search as get_swh_search
from swh.search.interface import SearchInterface
from swh.storage import get_storage as get_swh_storage
from swh.storage.interface import StorageInterface

from .client.view import explorer_page

graphql_cfg: Dict[str, Any] = {}
storage: Optional[StorageInterface] = None
search: Optional[SearchInterface] = None


def get_storage() -> StorageInterface:
    global storage
    if not storage:
        storage = get_swh_storage(**graphql_cfg["storage"])
    return storage


def get_search() -> SearchInterface:
    global search
    if not search:
        search = get_swh_search(**graphql_cfg["search"])
    return search


class AnonymousAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        return AuthCredentials(["anonymous"]), UnauthenticatedUser()


def load_and_check_config(config_path: Optional[str]) -> Dict[str, Any]:
    """Check the minimal configuration is set to run the api or raise an
       error explanation.

    Args:
        config_path: Path to the configuration file to load

    Raises:
        Error if the setup is not as expected

    Returns:
        configuration as a dict

    """
    if not config_path:
        raise EnvironmentError("Configuration file must be defined")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} does not exist")

    cfg = config.read(config_path)
    if "storage" not in cfg:
        raise KeyError("Missing 'storage' configuration")

    return cfg


def make_app_from_configfile():
    """Loading the configuration from a configuration file.

    SWH_CONFIG_FILENAME environment variable defines the
    configuration path to load.
    """
    from .app import schema, validation_rules
    from .errors import format_error, on_auth_error
    from .middlewares.logger import LogMiddleware

    global graphql_cfg

    if not graphql_cfg:
        config_path = os.environ.get("SWH_CONFIG_FILENAME")
        graphql_cfg = load_and_check_config(config_path)

    ariadne_app = GraphQL(
        schema,
        debug=graphql_cfg["debug"],
        introspection=graphql_cfg["introspection"],
        validation_rules=validation_rules,
        error_formatter=format_error,
    )

    if "auth" in graphql_cfg:
        auth_backend = BearerTokenAuthBackend(
            server_url=graphql_cfg["auth"]["server"],
            realm_name=graphql_cfg["auth"]["realm"],
            client_id=graphql_cfg["auth"]["client"],
            # FIXME, improve this with response cache implementation
            cache=Cache.from_url(url=graphql_cfg["auth"]["cache"]["url"]),
        )
    else:
        auth_backend = AnonymousAuthBackend()

    middleware = [
        Middleware(
            CORSMiddleware,
            # FIXME, restrict origins after deploying the JS client
            allow_origins=["*"],
            allow_methods=("GET", "POST", "OPTIONS"),
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=auth_backend,
            on_error=on_auth_error,
        ),
        Middleware(LogMiddleware),
    ]

    # Mount under a starlette application
    application = Starlette(
        routes=[
            Route("/", ariadne_app, methods=["POST"], name="graphql_api"),
            Route("/", explorer_page, methods=["GET"]),
        ],
        middleware=middleware,
    )
    return application
