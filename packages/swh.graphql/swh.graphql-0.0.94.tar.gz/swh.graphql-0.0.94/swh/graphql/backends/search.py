# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import Optional

from swh.graphql import server
from swh.search.interface import MinimalOriginDict, SearchInterface
from swh.storage.interface import PagedResult


class Search:
    def __init__(self):
        self.search: SearchInterface = server.get_search()

    def get_origins(
        self, query: str, after: Optional[str] = None, first: int = 50
    ) -> PagedResult[MinimalOriginDict]:
        return self.search.origin_search(
            url_pattern=query,
            page_token=after,
            limit=first,
        )
