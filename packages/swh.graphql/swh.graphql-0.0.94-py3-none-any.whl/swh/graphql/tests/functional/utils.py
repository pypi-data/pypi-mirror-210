# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import json
from typing import Dict, Tuple

from ariadne import gql


def get_query_response(
    client, query_str: str, response_code: int = 200, **kwargs
) -> Tuple[Dict, Dict]:
    query = gql(query_str)
    response = client.post("/", json={"query": query, "variables": kwargs})
    assert response.status_code == response_code, response.content
    result = json.loads(response.content)
    return result.get("data"), result.get("errors")


def assert_missing_object(client, query_str: str, obj_type: str, **kwargs) -> None:
    data, errors = get_query_response(client, query_str, **kwargs)
    assert data[obj_type] is None
    assert len(errors) == 1
    assert errors[0]["message"] == "Object error: Requested object is not available"
    assert errors[0]["path"] == [obj_type]


def get_error_response(
    client, query_str: str, response_code: int = 200, **kwargs
) -> Dict:
    data, errors = get_query_response(
        client, query_str, response_code=response_code, **kwargs
    )
    assert len(errors) > 0
    return errors
