# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from collections import namedtuple
from typing import Any, ClassVar, Optional, Union

from graphql.type import GraphQLResolveInfo

from swh.graphql import resolvers as rs
from swh.graphql.backends.archive import Archive
from swh.graphql.errors import NullableObjectError, ObjectNotFoundError


class BaseNode:
    """
    Base resolver for all the nodes
    """

    _can_be_null: ClassVar[bool] = False

    def __init__(self, obj, info, node_data: Optional[Any] = None, **kwargs) -> None:
        self.obj: Optional[Union[BaseNode, rs.base_connection.BaseConnection]] = obj
        self.info: GraphQLResolveInfo = info
        self.kwargs = kwargs
        # initialize commonly used vars
        self.archive = Archive()
        self._node: Optional[Any] = self._get_node(node_data)
        # handle the errors, if any, after _node is set
        self._handle_node_errors()

    def _get_node(self, node_data: Optional[Any]) -> Optional[Any]:
        """
        Get the node object from the given data
        if the data (node_data) is none make a function call
        to get data from backend
        """
        if node_data is None:
            node_data = self._get_node_data()
        return self._get_node_from_data(node_data)

    def _get_node_from_data(self, node_data: Any) -> Optional[Any]:
        """
        Get the object from node_data
        In case of a dict, convert it to an object
        Override to support different data structures
        """
        if isinstance(node_data, dict):
            return namedtuple("NodeObj", node_data.keys())(*node_data.values())
        return node_data

    def _handle_node_errors(self) -> None:
        """
        Handle any error related to node data

        raise an error in case the object returned is None
        override for specific behaviour
        """
        if self._node is None and self._can_be_null:
            # fail silently
            raise NullableObjectError()
        elif self._node is None:
            # This will send this error to the client
            raise ObjectNotFoundError("Requested object is not available")

    def _get_node_data(self) -> Optional[Any]:
        """
        Override for desired behaviour
        This will be called only when node_data is None
        """
        # FIXME, make this call async (not for v1)

    def __getattr__(self, name: str) -> Any:
        """
        Any property defined in the sub-class will get precedence over
        the _node attributes
        """
        return getattr(self._node, name)

    def is_type_of(self) -> str:
        return self.__class__.__name__


class BaseSWHNode(BaseNode):
    """
    Base resolver for all the nodes with a SWHID field
    """

    @property
    def swhid(self):
        return self._node.swhid()
