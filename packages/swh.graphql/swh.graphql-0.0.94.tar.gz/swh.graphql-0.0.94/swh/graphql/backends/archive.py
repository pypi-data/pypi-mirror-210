# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

from swh.graphql import server
from swh.model.model import (
    Content,
    Directory,
    DirectoryEntry,
    Origin,
    OriginVisit,
    OriginVisitStatus,
    Release,
    Revision,
    Sha1Git,
    Snapshot,
    SnapshotBranch,
)
from swh.model.swhids import ObjectType
from swh.storage.algos.origin import origin_get_latest_visit_status
from swh.storage.algos.snapshot import snapshot_resolve_branch_target
from swh.storage.interface import (
    HashDict,
    ListOrder,
    PagedResult,
    PartialBranches,
    StorageInterface,
)


class Archive:
    def __init__(self) -> None:
        self.storage: StorageInterface = server.get_storage()

    def get_origin(self, url: str) -> Optional[Origin]:
        return list(self.storage.origin_get(origins=[url]))[0]

    def get_origins(
        self, after: Optional[str] = None, first: int = 50
    ) -> PagedResult[Origin]:
        return self.storage.origin_list(page_token=after, limit=first)

    def get_origin_visits(
        self,
        origin_url: str,
        order: ListOrder,
        after: Optional[str] = None,
        first: int = 50,
    ) -> PagedResult[OriginVisit]:
        return self.storage.origin_visit_get(
            origin=origin_url, page_token=after, limit=first, order=order
        )

    def get_origin_visit(self, origin_url: str, visit_id: int) -> Optional[OriginVisit]:
        return self.storage.origin_visit_get_by(origin=origin_url, visit=visit_id)

    def get_origin_latest_visit(
        self,
        origin_url: str,
        visit_type: Optional[str] = None,
        allowed_statuses: Optional[List[str]] = None,
        require_snapshot: bool = False,
    ) -> Optional[OriginVisit]:
        return self.storage.origin_visit_get_latest(
            origin=origin_url,
            type=visit_type,
            allowed_statuses=allowed_statuses,
            require_snapshot=require_snapshot,
        )

    def get_visit_statuses(
        self,
        origin_url: str,
        visit_id: int,
        order: ListOrder,
        after: Optional[str] = None,
        first: int = 50,
    ) -> PagedResult[OriginVisitStatus]:
        return self.storage.origin_visit_status_get(
            origin=origin_url,
            visit=visit_id,
            page_token=after,
            limit=first,
            order=order,
        )

    def get_latest_visit_status(
        self,
        origin_url: str,
        visit_id: int,
        allowed_statuses: Optional[List[str]] = None,
        require_snapshot: bool = False,
    ) -> Optional[OriginVisitStatus]:
        return self.storage.origin_visit_status_get_latest(
            origin_url=origin_url,
            visit=visit_id,
            allowed_statuses=allowed_statuses,
            require_snapshot=require_snapshot,
        )

    def get_origin_snapshots(self, origin_url: str) -> List[Sha1Git]:
        return self.storage.origin_snapshot_get_all(origin_url=origin_url)

    def get_snapshot(
        self, snapshot_id: Sha1Git, verify: bool = True
    ) -> Optional[Snapshot]:
        # FIXME, change to accept list of snapshot_ids if needed
        if verify and not self.is_object_available(
            object_id=snapshot_id, object_type=ObjectType.SNAPSHOT
        ):
            # verify is True and the object is missing in the archive
            return None
        # Return a Snapshot model object; branches is initialized as empty
        # Same pattern is used in get_directory
        return Snapshot(id=snapshot_id, branches={})

    def get_snapshot_branches(
        self,
        snapshot: Sha1Git,
        after: bytes = b"",
        first: int = 50,
        target_types: Optional[List[str]] = None,
        name_include: Optional[bytes] = None,
        name_exclude_prefix: Optional[bytes] = None,
    ) -> Optional[PartialBranches]:
        return self.storage.snapshot_get_branches(
            snapshot_id=snapshot,
            branches_from=after,
            branches_count=first,
            target_types=target_types,
            branch_name_include_substring=name_include,
            branch_name_exclude_prefix=name_exclude_prefix,
        )

    def get_revisions(self, revision_ids: List[Sha1Git]) -> List[Optional[Revision]]:
        return self.storage.revision_get(revision_ids=revision_ids)

    def get_revision_log(
        self, revision_ids: List[Sha1Git], first: int = 50
    ) -> Iterable[Optional[Dict[str, Any]]]:
        return self.storage.revision_log(revisions=revision_ids, limit=first)

    def get_releases(self, release_ids: List[Sha1Git]) -> List[Optional[Release]]:
        return self.storage.release_get(releases=release_ids)

    def get_directory(
        self, directory_id: Sha1Git, verify: bool = True
    ) -> Optional[Directory]:
        # FIXME, change to accept list of directory_ids if needed
        if verify and not self.is_object_available(
            object_id=directory_id, object_type=ObjectType.DIRECTORY
        ):
            # verify is True and the object is missing in the archive
            return None
        # Return a Directory model object; entries is initialized as empty
        # Same pattern is used in get_snapshot
        return Directory(id=directory_id, entries=())

    def get_directory_entry_by_path(
        self, directory_id: Sha1Git, path: str
    ) -> Optional[Dict[str, Any]]:
        paths = [x.encode() for x in path.strip(os.path.sep).split(os.path.sep)]
        return self.storage.directory_entry_get_by_path(
            directory=directory_id, paths=paths
        )

    def get_directory_entries(
        self, directory_id: Sha1Git, after: Optional[bytes] = None, first: int = 50
    ) -> Optional[PagedResult[DirectoryEntry]]:
        return self.storage.directory_get_entries(
            directory_id=directory_id, limit=first, page_token=after
        )

    def is_object_available(self, object_id: bytes, object_type: ObjectType) -> bool:
        mapping = {
            ObjectType.CONTENT: self.storage.content_missing_per_sha1_git,
            ObjectType.DIRECTORY: self.storage.directory_missing,
            ObjectType.RELEASE: self.storage.release_missing,
            ObjectType.REVISION: self.storage.revision_missing,
            ObjectType.SNAPSHOT: self.storage.snapshot_missing,
        }
        return not list(mapping[object_type]([object_id]))

    def get_contents(self, hashes: HashDict) -> List[Content]:
        return self.storage.content_find(content=hashes)

    # def get_content_data(self, content_sha1: Sha1) -> Optional[bytes]:
    #     return self.storage.content_get_data(content=content_sha1)

    def get_branch_target(
        self,
        snapshot_id: Sha1Git,
        branch_obj: Optional[SnapshotBranch],
        max_length: int,
    ) -> Tuple[Optional[SnapshotBranch], List[bytes]]:
        return snapshot_resolve_branch_target(
            storage=self.storage,
            snapshot_id=snapshot_id,
            branch_obj=branch_obj,
            max_length=max_length,
        )

    def get_latest_origin_visit_status(
        self, origin: str, require_snapshot: bool = True
    ):
        return origin_get_latest_visit_status(
            storage=self.storage, origin_url=origin, require_snapshot=require_snapshot
        )
