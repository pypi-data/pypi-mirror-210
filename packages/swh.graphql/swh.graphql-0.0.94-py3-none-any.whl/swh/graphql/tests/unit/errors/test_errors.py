# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from graphql import GraphQLError, GraphQLSyntaxError
import pytest
import sentry_sdk

from swh.graphql import errors


def test_errors():
    err = errors.ObjectNotFoundError("test error")
    assert str(err) == "Object error: test error"

    err = errors.PaginationError("test error")
    assert str(err) == "Pagination error: test error"

    err = errors.InvalidInputError("test error")
    assert str(err) == "Input error: test error"


def test_format_error_with_debug():
    err = GraphQLError("test error")
    response = errors.format_error(err, debug=True)
    assert "extensions" in response


def test_format_error_without_debug():
    err = GraphQLError("test error")
    response = errors.format_error(err)
    assert "extensions" not in response


def test_format_error_sent_to_sentry(mocker):
    mocked_senty_call = mocker.patch.object(sentry_sdk, "capture_exception")
    err = GraphQLError("test error")
    err.original_error = NameError("test error")  # not an expected error
    errors.format_error(err)
    mocked_senty_call.assert_called_once_with(err)


@pytest.mark.parametrize(
    "error",
    [errors.ObjectNotFoundError, errors.PaginationError, errors.InvalidInputError],
)
def test_format_error_skip_sentry(mocker, error):
    mocked_senty_call = mocker.patch.object(sentry_sdk, "capture_exception")
    err = GraphQLError("test error")
    err.original_error = error("test error")
    errors.format_error(err)
    mocked_senty_call.assert_not_called()


def test_format_error_query_syntax_error_skip_sentry(mocker):
    mocked_senty_call = mocker.patch.object(sentry_sdk, "capture_exception")
    error = GraphQLSyntaxError(source=None, position=[1], description="test")
    errors.format_error(error)
    mocked_senty_call.assert_not_called()
