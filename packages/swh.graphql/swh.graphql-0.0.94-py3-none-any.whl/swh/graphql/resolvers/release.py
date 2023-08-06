# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from typing import Optional, Union

from swh.model.model import CoreSWHID, ObjectType
from swh.model.model import Release as ModelRelease
from swh.model.model import Sha1Git

from .base_node import BaseSWHNode


class BaseReleaseNode(BaseSWHNode):
    """
    Base resolver for all the release nodes
    """

    def _get_release_by_id(self, release_id: Sha1Git) -> Optional[ModelRelease]:
        releases = self.archive.get_releases([release_id])
        return releases[0] if releases else None

    def target_hash(self) -> Optional[Sha1Git]:
        assert self._node is not None
        return self._node.target

    def target_type(self) -> ObjectType:
        assert self._node is not None
        return self._node.target_type

    def is_type_of(self) -> str:
        # is_type_of is required only when resolving a UNION type
        # This is for ariadne to return the right type
        return "Release"


class ReleaseNode(BaseReleaseNode):
    """
    Node resolver for a release requested directly with its SWHID
    """

    def _get_node_data(self) -> Optional[ModelRelease]:
        release_swhid = self.kwargs.get("swhid")
        assert isinstance(release_swhid, CoreSWHID)
        return self._get_release_by_id(release_swhid.object_id)


class TargetReleaseNode(BaseReleaseNode):
    """
    Node resolver for a release requested as a target
    """

    from .target import BranchTargetNode, TargetNode

    _can_be_null = True
    obj: Union[TargetNode, BranchTargetNode]

    def _get_node_data(self) -> Optional[ModelRelease]:
        # self.obj.target_hash is the requested release id
        return self._get_release_by_id(self.obj.target_hash)
