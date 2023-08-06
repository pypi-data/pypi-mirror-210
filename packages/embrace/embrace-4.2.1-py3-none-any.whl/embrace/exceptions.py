#  Copyright 2020 Oliver Cope
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


class InvalidStatement(Exception):
    """
    The statement could not be parsed
    """


class NoResultFound(Exception):
    """
    A row was expected but the query did not generate one
    """


class MultipleResultsFound(Exception):
    """
    A single row was expected but the query returned multiple rows
    """


class ConnectionLimitError(Exception):
    """
    The connection pool has run out of available connections
    """


class Error(Exception):
    """
    The PEP-249 base error class
    """


class InterfaceError(Error):
    """
    PEP-249 error
    """


class DatabaseError(Error):
    """
    PEP-249 error
    """


class DataError(DatabaseError):
    """
    PEP-249 error
    """


class OperationalError(DatabaseError):
    """
    PEP-249 error
    """


class IntegrityError(DatabaseError):
    """
    PEP-249 error
    """


class InternalError(DatabaseError):
    """
    PEP-249 error
    """


class ProgrammingError(DatabaseError):
    """
    PEP-249 error
    """


class NotSupportedError(DatabaseError):
    """
    PEP-249 error
    """


pep_249_exceptions = [
    Error,
    InterfaceError,
    DatabaseError,
    DataError,
    OperationalError,
    IntegrityError,
    InterfaceError,
    ProgrammingError,
    NotSupportedError,
]
pep_249_exception_names = {c.__name__: c for c in pep_249_exceptions}
