# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import Union

from ariadne import format_error as original_format_error
from graphql import GraphQLError, GraphQLSyntaxError
import sentry_sdk
from starlette.requests import Request
from starlette.responses import JSONResponse

from .errors import InvalidInputError, ObjectNotFoundError, PaginationError


def format_error(error: Union[GraphQLError, GraphQLSyntaxError], debug: bool = False):
    """
    Response error formatting
    """
    original_format = original_format_error(error, debug)
    if debug:
        # If debug is enabled, reuse Ariadne's formatting logic with stack trace
        return original_format
    # Errors raised by ariadne and graphql-core, it is safe to skip query syntax errors
    expected_base_errors = (GraphQLSyntaxError,)
    expected_errors = (ObjectNotFoundError, PaginationError, InvalidInputError)
    if not isinstance(error, expected_base_errors) and not isinstance(
        error.original_error, expected_errors
    ):
        # a crash, send to sentry
        sentry_sdk.capture_exception(error)
    formatted = error.formatted
    formatted["message"] = error.message
    # FIXME log the original_format to kibana (with stack trace)
    return formatted


def on_auth_error(request: Request, exc: Exception):
    # this error is raised outside the resolver context
    # using the default error formatter to log in sentry
    wrapped_error = GraphQLError("Authentication error", original_error=exc)
    return JSONResponse({"errors": [format_error(wrapped_error)]}, status_code=401)
