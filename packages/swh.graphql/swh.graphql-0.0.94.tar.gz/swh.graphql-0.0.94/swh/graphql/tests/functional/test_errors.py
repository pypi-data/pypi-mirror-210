"""
# Copyright (C) 2023 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information
"""

from . import utils


def test_auth_error(client, authentication_error):
    query_str = """
    query getOrigin($url: String!) {
      origin(url: $url) {
        url
      }
    }
    """
    errors = utils.get_error_response(
        client, query_str, response_code=401, url="http://example.com"
    )
    assert "Authentication error" in errors[0]["message"]
