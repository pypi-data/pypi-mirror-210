# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import datetime

from swh.model.model import (
    Directory,
    DirectoryEntry,
    ObjectType,
    OriginVisitStatus,
    Release,
    Revision,
    RevisionType,
    Snapshot,
    SnapshotBranch,
    TargetType,
)
from swh.model.tests import swh_model_data

UTC = datetime.timezone.utc


def populate_search_data(search):
    search.origin_update({"url": origin.url} for origin in get_origins())


def get_origins():
    return swh_model_data.ORIGINS


def get_visits():
    return swh_model_data.ORIGIN_VISITS


def get_visit_status():
    return swh_model_data.ORIGIN_VISIT_STATUSES


def get_snapshots():
    return swh_model_data.SNAPSHOTS


def get_releases():
    return swh_model_data.RELEASES


def get_revisions():
    return swh_model_data.REVISIONS


def get_contents():
    return swh_model_data.CONTENTS


def get_directories():
    return swh_model_data.DIRECTORIES


def get_releases_with_target():
    """
    GraphQL will not return a target object unless the target id
    is present in the DB.
    Return release objects with real targets instead of dummy
    targets in swh.model.tests.swh_model_data
    """
    with_revision = Release(
        name=b"v0.0.1",
        target_type=ObjectType.REVISION,
        target=get_revisions()[0].id,
        message=b"foo",
        synthetic=False,
    )
    with_release = Release(
        name=b"v0.0.1",
        target_type=ObjectType.RELEASE,
        target=get_releases()[0].id,
        message=b"foo",
        synthetic=False,
    )
    with_directory = Release(
        name=b"v0.0.1",
        target_type=ObjectType.DIRECTORY,
        target=get_directories()[0].id,
        message=b"foo",
        synthetic=False,
    )
    with_content = Release(
        name=b"v0.0.1",
        target_type=ObjectType.CONTENT,
        target=get_contents()[0].sha1_git,
        message=b"foo",
        synthetic=False,
    )
    return [with_revision, with_release, with_directory, with_content]


def get_releases_with_empty_target():
    return [
        Release(
            name=b"v0.0.1",
            target_type=ObjectType.REVISION,
            target=b"",
            message=b"foo",
            synthetic=False,
        )
    ]


def get_revisions_with_parents():
    """
    Revisions with real revisions as parents
    """
    return [
        Revision(
            message=b"hello",
            date=swh_model_data.DATES[0],
            committer=swh_model_data.COMMITTERS[0],
            author=swh_model_data.COMMITTERS[0],
            committer_date=swh_model_data.DATES[0],
            type=RevisionType.GIT,
            directory=b"\x01" * 20,
            synthetic=False,
            parents=(get_revisions()[0].id, get_revisions()[1].id),
        )
    ]


def get_revisions_with_none_date():
    return [
        Revision(
            message=b"hello",
            date=None,
            committer=swh_model_data.COMMITTERS[0],
            author=swh_model_data.COMMITTERS[0],
            committer_date=swh_model_data.DATES[0],
            type=RevisionType.GIT,
            directory=b"\x01" * 20,
            synthetic=False,
            parents=(get_revisions()[0].id, get_revisions()[1].id),
        )
    ]


def get_directories_with_nested_path():
    return [
        Directory(
            entries=(
                DirectoryEntry(
                    name=b"sub-dir",
                    perms=0o644,
                    type="dir",
                    target=get_directories()[1].id,
                ),
            )
        )
    ]


def get_directories_with_special_name_entries():
    return [
        Directory(
            entries=(
                DirectoryEntry(
                    name="ßßétEÉt".encode(),
                    perms=0o644,
                    type="file",
                    target=get_contents()[0].sha1_git,
                ),
            )
        )
    ]


def get_visit_with_multiple_status():
    return [
        OriginVisitStatus(
            origin=get_origins()[0].url,
            date=datetime.datetime(2014, 5, 7, 4, 20, 39, 432222, tzinfo=UTC),
            visit=1,
            type="git",
            status="ongoing",
            snapshot=None,
            metadata=None,
        )
    ]


def get_snapshots_with_multiple_alias():
    return [
        Snapshot(
            # This branch alias chain breaks without a target
            branches={
                b"target/alias1": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/alias2"
                ),
                b"target/alias2": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/alias3"
                ),
            },
        ),
        Snapshot(
            # This branch alias chain resolves to a release after 2 levels
            branches={
                b"target/alias1": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/alias2"
                ),
                b"target/alias2": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/release"
                ),
                b"target/release": SnapshotBranch(
                    target_type=TargetType.RELEASE, target=get_releases()[0].id
                ),
            },
        ),
        Snapshot(
            # This branch alias chain is going 6 levels deep
            branches={
                b"target/alias1": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/alias2"
                ),
                b"target/alias2": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/alias3"
                ),
                b"target/alias3": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/alias4"
                ),
                b"target/alias4": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/alias5"
                ),
                b"target/alias5": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/alias6"
                ),
                b"target/alias6": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/release"
                ),
                b"target/release": SnapshotBranch(
                    target_type=TargetType.RELEASE, target=get_releases()[0].id
                ),
            },
        ),
        Snapshot(
            # This branch alias chain is recursive
            branches={
                b"target/alias1": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/alias2"
                ),
                b"target/alias2": SnapshotBranch(
                    target_type=TargetType.ALIAS, target=b"target/alias1"
                ),
            },
        ),
    ]


GRAPHQL_EXTRA_TEST_OBJECTS = {
    "snapshot": get_snapshots_with_multiple_alias(),
    "release": get_releases_with_target() + get_releases_with_empty_target(),
    "revision": get_revisions_with_parents() + get_revisions_with_none_date(),
    "directory": get_directories_with_nested_path()
    + get_directories_with_special_name_entries(),
    "origin_visit_status": get_visit_with_multiple_status(),
}


def populate_dummy_data(storage):
    for object_type, objects in swh_model_data.TEST_OBJECTS.items():
        method = getattr(storage, object_type + "_add")
        method(objects)
    for object_type, objects in GRAPHQL_EXTRA_TEST_OBJECTS.items():
        method = getattr(storage, object_type + "_add")
        method(objects)
