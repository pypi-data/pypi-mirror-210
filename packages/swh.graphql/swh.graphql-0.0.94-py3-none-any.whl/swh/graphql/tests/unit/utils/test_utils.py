# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import datetime

from swh.graphql.utils import utils


class TestUtils:
    def test_get_b64_string(self):
        assert utils.get_b64_string("testing") == "dGVzdGluZw=="

    def test_get_b64_string_binary(self):
        assert utils.get_b64_string(b"testing") == "dGVzdGluZw=="

    def test_get_encoded_cursor_is_none(self):
        assert utils.get_encoded_cursor(None) is None

    def test_get_encoded_cursor(self):
        assert utils.get_encoded_cursor(None) is None
        assert utils.get_encoded_cursor("testing") == "dGVzdGluZw=="

    def test_get_decoded_cursor_is_none(self):
        assert utils.get_decoded_cursor(None) is None

    def test_get_decoded_cursor(self):
        assert utils.get_decoded_cursor("dGVzdGluZw==") == "testing"

    def test_get_formatted_date(self):
        date = datetime.datetime(
            2015, 8, 4, 22, 26, 14, 804009, tzinfo=datetime.timezone.utc
        )
        assert utils.get_formatted_date(date) == "2015-08-04T22:26:14.804009+00:00"

    def test_get_local_paginated_data(self):
        source = [1, 2, 3, 4, 5]
        response = utils.get_local_paginated_data(source, first=50)
        assert response.paged_result.results == source
        assert response.paged_result.next_page_token is None

    def test_get_local_paginated_data_first_arg(self):
        source = [1, 2, 3, 4, 5]
        response = utils.get_local_paginated_data(source, first=2)
        assert response.paged_result.results == source[:2]
        assert response.paged_result.next_page_token == "2"

    def test_get_local_paginated_data_after_arg(self):
        source = [1, 2, 3, 4, 5]
        response = utils.get_local_paginated_data(source, first=2, after="2")
        assert response.paged_result.results == [3, 4]
        assert response.paged_result.next_page_token == "4"

        response = utils.get_local_paginated_data(source, first=2, after="3")
        assert response.paged_result.results == [4, 5]
        assert response.paged_result.next_page_token is None

    def test_get_local_paginated_data_endcursor_outside(self):
        source = [1, 2, 3, 4, 5]
        response = utils.get_local_paginated_data(source, first=2, after="10")
        assert response.paged_result.results == []
        assert response.paged_result.next_page_token is None
