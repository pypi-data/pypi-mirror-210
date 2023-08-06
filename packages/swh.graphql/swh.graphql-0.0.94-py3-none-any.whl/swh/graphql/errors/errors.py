# Copyright (C) 2022 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information


class ObjectNotFoundError(Exception):
    """ """

    msg: str = "Object error"

    def __init__(self, message, errors=None):
        super().__init__(f"{self.msg}: {message}")


class PaginationError(Exception):
    """ """

    msg: str = "Pagination error"

    def __init__(self, message, errors=None):
        super().__init__(f"{self.msg}: {message}")


class InvalidInputError(Exception):
    """ """

    msg: str = "Input error"

    def __init__(self, message, errors=None):
        super().__init__(f"{self.msg}: {message}")


class NullableObjectError(Exception):
    pass


class DataError(Exception):
    pass
