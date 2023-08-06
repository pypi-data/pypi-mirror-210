# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import Optional

from swh.graphql.utils import utils
from swh.model.model import Sha1Git

from .base_connection import BaseConnection, ConnectionData
from .base_node import BaseNode
from .visit import BaseVisitNode


class BaseVisitStatusNode(BaseNode):
    """
    Base resolver for all the visit-status nodes
    """

    def snapshot_id(self) -> Optional[Sha1Git]:
        assert self._node is not None
        if self._node.snapshot is None:
            return None
        return self._node.snapshot


class LatestVisitStatusNode(BaseVisitStatusNode):
    """
    Node resolver for a visit-status requested from a visit
    """

    _can_be_null = True
    obj: BaseVisitNode

    def _get_node_data(self):
        # self.obj.origin is the origin URL
        return self.archive.get_latest_visit_status(
            origin_url=self.obj.origin,
            visit_id=self.obj.visitId,
            allowed_statuses=self.kwargs.get("allowedStatuses"),
            require_snapshot=self.kwargs.get("requireSnapshot"),
        )


class VisitStatusConnection(BaseConnection):
    """
    Connection resolver for the visit-status objects in a visit
    """

    obj: BaseVisitNode
    _node_class = BaseVisitStatusNode

    def _get_connection_data(self) -> ConnectionData:
        # self.obj.origin is the origin URL
        return ConnectionData(
            paged_result=self.archive.get_visit_statuses(
                self.obj.origin,
                self.obj.visitId,
                after=self._get_after_arg(),
                first=self._get_first_arg(),
                order=utils.get_storage_list_order(self.kwargs.get("sort")),
            )
        )

    def _get_index_cursor(self, index: int, node: BaseVisitStatusNode):
        # Visit status is using a different cursor, hence the override
        return utils.get_encoded_cursor(utils.get_formatted_date(node.date))
