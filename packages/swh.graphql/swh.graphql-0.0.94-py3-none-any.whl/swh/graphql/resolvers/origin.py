# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from swh.model.model import Origin
from swh.storage.interface import PagedResult

from .base_connection import BaseConnection, ConnectionData
from .base_node import BaseSWHNode
from .search import OriginSearchResultNode


class BaseOriginNode(BaseSWHNode):
    pass


class OriginNode(BaseOriginNode):
    """
    Node resolver for an origin requested directly with its URL
    """

    def _get_node_data(self):
        return self.archive.get_origin(self.kwargs.get("url"))


class TargetOriginNode(BaseOriginNode):
    """
    Node resolver for an origin requested as a target
    """

    obj: OriginSearchResultNode
    _can_be_null = True

    def _get_node_data(self):
        # The target origin URL is guaranteed to exist in the archive
        # Hence returning the origin object without any explicit check in the archive
        # This assumes that the search index and archive are in sync
        if self.obj.target_url:
            return Origin(self.obj.target_url)
        return None


class OriginConnection(BaseConnection):
    """
    Connection resolver for the origins
    """

    _node_class = BaseOriginNode

    def _get_connection_data(self) -> ConnectionData:
        # Use the search backend if a urlPattern is given
        if self.kwargs.get("urlPattern"):
            origins = self.search.get_origins(
                query=self.kwargs.get("urlPattern"),
                after=self._get_after_arg(),
                first=self._get_first_arg(),
            )
            results = [Origin(ori["url"]) for ori in origins.results]
            paged_result = PagedResult(
                results=results, next_page_token=origins.next_page_token
            )
        else:
            # Use the archive backend by default
            paged_result = self.archive.get_origins(
                after=self._get_after_arg(), first=self._get_first_arg()
            )
        return ConnectionData(paged_result=paged_result)
