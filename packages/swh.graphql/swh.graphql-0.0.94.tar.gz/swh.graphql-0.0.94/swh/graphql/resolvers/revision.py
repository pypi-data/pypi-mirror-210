# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import Optional, Union

from swh.graphql.utils import utils
from swh.model.model import Revision, Sha1Git
from swh.model.swhids import CoreSWHID

from .base_connection import BaseConnection, ConnectionData
from .base_node import BaseSWHNode
from .target import BranchTargetNode, TargetNode


class BaseRevisionNode(BaseSWHNode):
    """
    Base resolver for all the revision nodes
    """

    def _get_revision_by_id(self, revision_id) -> Optional[Revision]:
        revisions = self.archive.get_revisions([revision_id])
        return revisions[0] if revisions else None

    @property
    def committerDate(self):  # To support the schema naming convention
        assert self._node is not None
        return self._node.committer_date

    @property
    def type(self) -> str:
        assert self._node is not None
        return self._node.type.value

    def is_type_of(self) -> str:
        # is_type_of is required only when resolving a UNION type
        # This is for ariadne to return the right type
        return "Revision"

    def directory_hash(self) -> Sha1Git:  # hash of the unique revision directory
        # To be used while resolving the revision directory
        assert self._node is not None
        return self._node.directory


class RevisionNode(BaseRevisionNode):
    """
    Node resolver for a revision requested directly with its SWHID
    """

    def _get_node_data(self) -> Optional[Revision]:
        revision_swhid = self.kwargs.get("swhid")
        assert isinstance(revision_swhid, CoreSWHID)
        return self._get_revision_by_id(revision_swhid.object_id)


class TargetRevisionNode(BaseRevisionNode):
    """
    Node resolver for a revision requested as a target
    """

    _can_be_null = True
    obj: Union[
        BranchTargetNode,
        TargetNode,
    ]

    def _get_node_data(self) -> Optional[Revision]:
        # self.obj.target_hash is the requested revision id
        return self._get_revision_by_id(self.obj.target_hash)


class ParentRevisionConnection(BaseConnection):
    """
    Connection resolver for parent revisions in a revision
    """

    obj: BaseRevisionNode

    _node_class = BaseRevisionNode

    def _get_connection_data(self) -> ConnectionData:
        # self.obj is the current(child) revision

        # FIXME, using dummy(local) pagination, move pagination to backend
        # STORAGE-TODO (pagination)
        parents = self.archive.get_revisions(self.obj.parents)
        return utils.get_local_paginated_data(
            parents, self._get_first_arg(), self._get_after_arg()
        )


class LogRevisionConnection(BaseConnection):
    """
    Connection resolver for the log (list of revisions) in a revision
    """

    obj: BaseRevisionNode

    _node_class = BaseRevisionNode

    def _get_connection_data(self) -> ConnectionData:
        log = self.archive.get_revision_log([self.obj.swhid.object_id])
        # Storage is returning a list of dicts instead of model objects
        # Following loop is to reverse that operation
        # STORAGE-TODO; remove to_dict from storage.revision_log
        log = [Revision.from_dict(rev) for rev in log]
        # FIXME, using dummy(local) pagination, move pagination to backend
        # STORAGE-TODO (pagination)
        return utils.get_local_paginated_data(
            log, self._get_first_arg(), self._get_after_arg()
        )
