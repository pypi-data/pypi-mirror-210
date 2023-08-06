# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from abc import ABC, abstractmethod
import binascii
from dataclasses import dataclass
from typing import Any, List, Optional, Type, Union

from graphql.type import GraphQLResolveInfo

from swh.graphql.backends.archive import Archive
from swh.graphql.backends.search import Search
from swh.graphql.errors import PaginationError
from swh.graphql.utils import utils
from swh.storage.interface import PagedResult

from .base_node import BaseNode


@dataclass
class PageInfo:
    hasNextPage: bool
    endCursor: Optional[str]


@dataclass
class ConnectionEdge:
    node: Any
    cursor: Optional[str]


@dataclass
class ConnectionData:
    paged_result: PagedResult
    total_count: Optional[int] = None


class BaseConnection(ABC):
    """
    Base resolver for all the connections
    """

    _node_class: Optional[Type[BaseNode]] = None
    _page_size: int = 50  # default page size (default value for the first arg)
    _max_page_size: int = 1000  # maximum page size(max value for the first arg)

    def __init__(self, obj, info, data=None, **kwargs):
        self.obj: Optional[BaseNode] = obj
        self.info: GraphQLResolveInfo = info
        self._connection_data: ConnectionData = data
        self.kwargs = kwargs
        # initialize commonly used vars
        self.archive = Archive()
        self.search = Search()

    @property
    def edges(self) -> List[ConnectionEdge]:
        """
        Return the list of connection edges, each with a cursor
        """
        return [
            ConnectionEdge(node=node, cursor=self._get_index_cursor(index, node))
            for (index, node) in enumerate(self.nodes)
        ]

    @property
    def nodes(self) -> List[Union[BaseNode, object]]:
        """
        Override if needed; return a list of objects

        If a node class is set, return a list of its (Node) instances
        else a list of raw results
        """
        if self._node_class is not None:
            return [
                self._node_class(
                    obj=self, info=self.info, node_data=result, **self.kwargs
                )
                for result in self.get_connection_data().paged_result.results
            ]
        return self.get_connection_data().paged_result.results

    @property
    def pageInfo(self) -> PageInfo:  # To support the schema naming convention
        # FIXME, add more details like startCursor
        return PageInfo(
            hasNextPage=bool(self.get_connection_data().paged_result.next_page_token),
            endCursor=utils.get_encoded_cursor(
                self.get_connection_data().paged_result.next_page_token
            ),
        )

    @property
    def totalCount(self) -> Optional[int]:  # To support the schema naming convention
        """
        Will be None for most of the connections
        override if needed/possible
        """
        return self.get_connection_data().total_count

    def get_connection_data(self) -> ConnectionData:
        """
        Cache to avoid multiple calls to the backend :meth:`_get_connection_data`
        """
        if self._connection_data is None:
            # FIXME, make this call async (not for v1)
            self._connection_data = self._get_connection_data()
        return self._connection_data

    @abstractmethod
    def _get_connection_data(self) -> ConnectionData:
        """
        Override to fetch data
        """
        # FIXME, make this call async (not for v1)

    def _get_after_arg(self):
        """
        Return the decoded next page token. Override to support a different
        cursor type
        """
        # different implementation is used in SnapshotBranchConnection
        try:
            cursor = utils.get_decoded_cursor(self.kwargs.get("after"))
        except (UnicodeDecodeError, binascii.Error) as e:
            raise PaginationError("Invalid value for argument 'after'", errors=e)
        return cursor

    def _get_first_arg(self) -> int:
        """ """
        # page_size is set to 50 by default
        # Input type check is not required; It is defined in schema as an int
        first = self.kwargs.get("first", self._page_size)
        if first < 0 or first > self._max_page_size:
            raise PaginationError(
                f"Value for argument 'first' is invalid; it must be between 0 and {self._max_page_size}"  # noqa: B950
            )
        return first

    def _get_index_cursor(self, index: int, node: Any) -> Optional[str]:
        """
        Get the cursor to the given item index
        """
        # default implementation which works with swh-storage pagaination
        # override this function to support other types (eg: SnapshotBranchConnection)
        offset_index = self._get_after_arg() or "0"
        index_cursor = int(offset_index) + index
        return utils.get_encoded_cursor(str(index_cursor))


class BaseList(ABC):
    """
    Base class to be used for simple lists that do not require
    pagination; eg resolveSWHID entrypoint
    """

    _node_class: Optional[Type[BaseNode]] = None

    def __init__(self, obj, info, results=None, **kwargs):
        self.obj: Optional[BaseNode] = obj
        self.info: GraphQLResolveInfo = info
        self.kwargs = kwargs
        self._results: List = results

        self.archive = Archive()

    def get_results(self) -> Optional[List[Any]]:
        if self._results is None:
            # To avoid multiple calls to the backend
            self._results = self._get_results()

        if self._node_class is not None:
            # convert list items to node objects
            return [
                self._node_class(
                    obj=self.obj, info=self.info, node_data=result, **self.kwargs
                )
                for result in self._results
            ]
        return self._results

    @abstractmethod
    def _get_results(self) -> Optional[List]:
        """
        Override for desired behaviour
        return a list of objects
        """
