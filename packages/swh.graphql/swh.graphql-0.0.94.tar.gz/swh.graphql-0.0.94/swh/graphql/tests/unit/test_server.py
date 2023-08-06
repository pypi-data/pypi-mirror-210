# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import pytest

from swh.graphql import server


def test_load_and_check_config_no_config():
    with pytest.raises(EnvironmentError):
        server.load_and_check_config(config_path=None)


def test_load_and_check_config_missing_config_file():
    with pytest.raises(FileNotFoundError):
        server.load_and_check_config(config_path="invalid")


def test_load_and_check_config_missing_storage_config(mocker):
    mocker.patch("swh.core.config.read", return_value={"test": "test"})
    with pytest.raises(KeyError):
        server.load_and_check_config(config_path="/tmp")


def test_load_and_check_config(mocker):
    mocker.patch("swh.core.config.read", return_value={"storage": {"test": "test"}})
    cfg = server.load_and_check_config(config_path="/tmp")
    assert cfg == {"storage": {"test": "test"}}
