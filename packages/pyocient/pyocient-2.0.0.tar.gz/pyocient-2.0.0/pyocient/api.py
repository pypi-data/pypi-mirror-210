#!/usr/bin/env python3

import configparser
import datetime
import decimal
import ipaddress
import logging
import re
import socket
import ssl
import struct

# pylint: disable=too-many-lines
import sys
import uuid
from collections import namedtuple
from math import isinf
from time import sleep, time_ns
from types import TracebackType
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from warnings import warn

import dsnparse  # type: ignore
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac, padding, serialization
from cryptography.hazmat.primitives.asymmetric.dh import DHPublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from google.protobuf.message import Message

from pyocient.pkg_version import __version__ as version

_T = TypeVar("_T")
_MsgT = TypeVar("_MsgT", bound=Message)

logger = logging.getLogger("pyocient")

# See PEP 249 for the values of these attributes
apilevel = "2.0"  # pylint: disable=invalid-name
threadsafety = 1  # pylint: disable=invalid-name
paramstyle = "pyformat"  # pylint: disable=invalid-name
DRIVER_ID = "pyocient"
PROTOCOL_VERSION = "7.0.1"
SESSION_EXPIRED_CODE = -733

parts = version.split(".")
version_major = int(parts[0])
version_minor = int(parts[1])


class SQLException(Exception):
    """Base exception for all Ocient exceptions.

    Attributes:

    - sql_state: The SQLSTATE defined in the SQL standard
    - reason: A string description of the exception
    - vendor_code: An Ocient specific error code
    """

    def __init__(self, reason: str = "", sql_state: str = "00000", vendor_code: int = 0) -> None:
        super().__init__()
        self.sql_state = sql_state
        self.reason = reason
        self.vendor_code = vendor_code

    def __str__(self) -> str:
        return f"State: {self.sql_state} Code: {self.vendor_code} Reason: {self.reason}"


#########################################################################
# Database API 2.0 exceptions.  These are required by PEM 249
#########################################################################


class Error(SQLException):
    """Exception that is the base class of all other error exceptions."""

    def __init__(self, reason: str, sql_state: str = "58005", vendor_code: int = -100) -> None:
        super().__init__(reason, sql_state=sql_state, vendor_code=vendor_code)


class Warning(SQLException):  # pylint: disable=redefined-builtin
    """Exception that is the base class of all other warning exceptions."""


class InterfaceError(Error):
    """Exception raised for errors that are related to the
    database interface rather than the database itself.
    """


class DatabaseError(Error):
    """Exception raised for errors that are related to the database."""


class InternalError(DatabaseError):
    """Exception raised when the database encounters an internal error,
    e.g. the cursor is not valid anymore
    """


class OperationalError(DatabaseError):
    """Exception raised for errors that are related to the database's
    operation and not necessarily under the control of the programmer,
    e.g. an unexpected disconnect occurs, the data source name is not found.
    """


class ProgrammingError(DatabaseError):
    """Exception raised for programming errors, e.g. table not found,
    syntax error in the SQL statement, wrong number of parameters
    specified, etc.
    """


class IntegrityError(DatabaseError):
    """Exception raised when the relational integrity of the database
    is affected, e.g. a foreign key check fails
    """


class DataError(DatabaseError):
    """Exception raised for errors that are due to problems with the
    processed data like division by zero, numeric value out of range, etc.
    """


class NotSupportedError(DatabaseError):
    """Exception raised in case a method or database API was used which is not
    supported by the database
    """


class MalformedURL(DatabaseError):
    """Exception raised in case a malformed DSN is received"""

    def __init__(self, reason: str) -> None:
        super().__init__(sql_state="08001", vendor_code=-200, reason=reason)


class TypeCodes:  # pylint: disable=too-few-public-methods
    """
    Database column type codes

    :meta private:
    """

    DEM = 0
    INT = 1
    LONG = 2
    FLOAT = 3
    DOUBLE = 4
    STRING = 5
    CHAR = 5
    TIMESTAMP = 6
    NULL = 7
    BOOLEAN = 8
    BINARY = 9
    BYTE = 10
    SHORT = 11
    TIME = 12
    DECIMAL = 13
    ARRAY = 14
    UUID = 15
    ST_POINT = 16
    IP = 17
    IPV4 = 18
    DATE = 19
    TIMESTAMP_NANOS = 20
    TIME_NANOS = 21
    TUPLE = 22
    ST_LINESTRING = 23
    ST_POLYGON = 24

    @classmethod
    def to_type(cls, typestr: str) -> int:
        """Given a string type, return its type code"""
        if hasattr(cls, typestr):
            attr = getattr(cls, typestr)
            if isinstance(attr, int):
                return attr
        raise Error(f"Unknown column type {typestr}")

    @classmethod
    def cls_to_type(cls, pclass: object) -> int:
        if pclass == str:
            return cls.STRING
        elif pclass == int:
            return cls.INT
        elif pclass == float:
            return cls.FLOAT
        elif pclass == uuid.UUID:
            return cls.UUID
        elif pclass == Optional[uuid.UUID]:
            return cls.UUID
        raise Error(f"Unknown column class {pclass}")


# By instantiating these here we reduce the overhead of setting this up
# each time we call it
_unpack_short = struct.Struct("!h").unpack_from
_unpack_int = struct.Struct("!i").unpack_from
_unpack_long = struct.Struct("!q").unpack_from
_unpack_float = struct.Struct("!f").unpack_from
_unpack_double = struct.Struct("!d").unpack_from
_unpack_bool = struct.Struct("?").unpack_from
_unpack_char = struct.Struct("c").unpack_from

# easy conversions we can do with structs
_type_map = {
    TypeCodes.INT: (struct.calcsize("!i"), _unpack_int),
    TypeCodes.LONG: (struct.calcsize("!q"), _unpack_long),
    TypeCodes.FLOAT: (struct.calcsize("!f"), _unpack_float),
    TypeCodes.DOUBLE: (struct.calcsize("!d"), _unpack_double),
    TypeCodes.BOOLEAN: (struct.calcsize("?"), _unpack_bool),
    TypeCodes.SHORT: (struct.calcsize("!h"), _unpack_short),
}


#########################################################################
# Database API 2.0 types.  These are required by PEM 249
#########################################################################
Binary = bytes  # : :meta private:
STRING = TypeCodes.STRING  # : :meta private:
BINARY = TypeCodes.BINARY  # : :meta private:
NUMBER = TypeCodes.INT  # : :meta private:
DATETIME = TypeCodes.TIMESTAMP  # : :meta private:
ROWID = TypeCodes.INT  # : :meta private:

#########################################################################
# Import our google protobuf message definitions
#########################################################################
try:
    from sharedMessages import clientWireProtocol_pb2 as proto
except ImportError:
    import pyocient.ClientWireProtocol_pb2 as proto

#########################################################################
# Lightweight GIS classes
#########################################################################


class _STPoint:
    def __init__(self, long: float, lat: float) -> None:
        self.long = long
        self.lat = lat

    def wkt_inner(self) -> str:
        return str(self.long) + " " + str(self.lat)

    def __repr__(self) -> str:
        if isinf(self.long) or isinf(self.lat):
            return "POINT EMPTY"
        return "POINT(" + self.wkt_inner() + ")"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _STPoint):
            return self.long == other.long and self.lat == other.lat
        return NotImplemented


def _linestring_wkt_inner(points: List[_STPoint]) -> str:
    return "(" + ", ".join((p.wkt_inner() for p in points)) + ")"


class _STLinestring:
    def __init__(self, points: List[_STPoint]) -> None:
        self.points = points

    def __repr__(self) -> str:
        if not self.points:
            return "LINESTRING EMPTY"
        return "LINESTRING" + _linestring_wkt_inner(self.points)

    def __eq__(self, other: object) -> bool:
        # strict equality, not semantic
        if isinstance(other, _STLinestring):
            return self.points == other.points
        return NotImplemented


class _STPolygon:
    def __init__(self, exterior: List[_STPoint], holes: List[List[_STPoint]]) -> None:
        self.exterior = exterior
        self.holes = holes

    def __repr__(self) -> str:
        if not self.exterior:
            return "POLYGON EMPTY"
        return "POLYGON(" + ", ".join((_linestring_wkt_inner(pl) for pl in [self.exterior] + self.holes)) + ")"

    def __eq__(self, other: object) -> bool:
        # strict equality, not semantic
        if isinstance(other, _STPolygon):
            return self.exterior == other.exterior and self.holes == other.holes
        return NotImplemented


#########################################################################
# Build supported request/response type mappings
#########################################################################


class _OcientRequestFactory(Generic[_T]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated request protobuf"""
        raise NotImplementedError

    def response(self) -> _T:
        """Generates a fully populated response protobuf"""
        raise NotImplementedError

    def process(self, rsp: _T) -> Any:
        """Process the client response"""
        raise NotImplementedError


class _ExecuteQueryFactory(_OcientRequestFactory[proto.ExecuteQueryResponse]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated EXECUTE_QUERY request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("EXECUTE_QUERY")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        req.execute_query.sql = operation
        req.execute_query.force = False
        return req

    def response(self) -> proto.ExecuteQueryResponse:
        """Generates a fully populated EXECUTE_QUERY response protobuf"""
        return proto.ExecuteQueryResponse()


class _ExecuteExplainFactory(_OcientRequestFactory[proto.ExplainResponseStringPlan]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated EXECUTE_EXPLAIN request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("EXECUTE_EXPLAIN")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        req.execute_explain.format = proto.ExplainFormat.JSON  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        splitted = operation.split(maxsplit=1)
        if len(splitted) == 2:
            req.execute_explain.sql = splitted[1]
        return req

    def response(self) -> proto.ExplainResponseStringPlan:
        """Generates a fully populated EXECUTE_EXPLAIN response protobuf"""
        return proto.ExplainResponseStringPlan()


class _ExecuteExportFactory(_OcientRequestFactory[proto.ExecuteExportResponse]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated EXECUTE_EXPORT request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("EXECUTE_EXPORT")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        req.execute_export.sql = operation
        return req

    def response(self) -> proto.ExecuteExportResponse:
        """Generates a fully populated EXECUTE_EXPORT response protobuf"""
        return proto.ExecuteExportResponse()


class _ExplainPipelineFactory(_OcientRequestFactory[proto.ExplainPipelineResponse]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated EXPLAIN_PIPELINE request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("EXPLAIN_PIPELINE")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        req.explain_pipeline.sql = operation
        return req

    def response(self) -> proto.ExplainPipelineResponse:
        """Generates a fully populated EXPLAIN_PIPELINE response protobuf"""
        return proto.ExplainPipelineResponse()


class _CheckDataFactory(_OcientRequestFactory[proto.CheckDataResponse]):
    """NOTE: this command is deprecated"""

    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated CHECK_DATA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("CHECK_DATA")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        req.check_data.sql = operation
        return req

    def response(self) -> proto.CheckDataResponse:
        """Generates a fully populated CHECK_DATA response protobuf"""
        return proto.CheckDataResponse()


class _ForceExternalFactory(_OcientRequestFactory[proto.ConfirmationResponse]):
    def request(self, operation: str) -> proto.Request:
        """Generates a fully populated FORCE_EXTERNAL request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("SET_PARAMETER")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        sp = req.set_parameter
        if operation.endswith("on"):
            sp.force_external.is_on = True
        elif operation.endswith("off"):
            sp.force_external.is_on = False
        else:
            raise ProgrammingError('Format must be "FORCE EXTERNAL (on|off)"')
        return req

    def response(self) -> proto.ConfirmationResponse:
        """Generates a fully populated FORCE_EXTERNAL response protobuf"""
        return proto.ConfirmationResponse()


class _SetSchemaFactory(_OcientRequestFactory[proto.ConfirmationResponse]):
    def request(self, schema: str) -> proto.Request:
        """Generates a fully populated SET SCHEMA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("SET_SCHEMA")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        req.set_schema.schema = schema
        return req

    def response(self) -> proto.ConfirmationResponse:
        """Generates SET_SCHEMA response protobuf"""
        return proto.ConfirmationResponse()


class _GetSchemaFactory(_OcientRequestFactory[proto.GetSchemaResponse]):
    def request(self) -> proto.Request:  # type: ignore
        """Generates a fully populated GET SCHEMA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("GET_SCHEMA")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        return req

    def response(self) -> proto.GetSchemaResponse:
        """Generates SET_SCHEMA response protobuf"""
        return proto.GetSchemaResponse()


class _ClearCacheFactory(_OcientRequestFactory[proto.ConfirmationResponse]):
    def request(self) -> proto.Request:  # type: ignore
        """Generates a fully populated CLEAR CACHE request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("CLEAR_CACHE")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        req.clear_cache.all_nodes = True
        return req

    def response(self) -> proto.ConfirmationResponse:
        """Generates SET_SCHEMA response protobuf"""
        return proto.ConfirmationResponse()


class _SetParameterFactory(_OcientRequestFactory[proto.ConfirmationResponse]):
    def request(self, op: str, val: Union[int, str, float]) -> proto.Request:  # type: ignore
        """Generates a fully populated SET PARAMETER request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("SET_PARAMETER")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240

        sp = req.set_parameter

        if type(val) == str and val.lower() == "reset":
            # Resets handled in cmdCompServer. Set val to 0 as a Parameter still needs to be set for flow control, and most require number values
            sp.reset = True
            val = 0 if op != "SERVICECLASS" else val

        # Set the appropriate parameter
        # proto field assignments are type checked at runtime
        if op == "MAXROWS":
            assert isinstance(val, int)
            sp.row_limit.rowLimit = val
        elif op == "MAXTIME":
            assert isinstance(val, int)
            sp.time_limit.timeLimit = val
        elif op == "MAXTEMPDISK":
            assert isinstance(val, int)
            sp.temp_disk_limit.tempDiskLimit = val
        elif op == "PRIORITY":
            assert isinstance(val, float)
            sp.priority.priority = val
        elif op == "PARALLELISM":
            assert isinstance(val, int)
            sp.concurrency.concurrency = val
        elif op == "SERVICECLASS":
            assert isinstance(val, str)
            sp.service_class_name.service_class_name = val
        elif op == "PSO":
            assert isinstance(val, int)
            sp.pso_threshold.threshold = val
        elif op == "ADJUSTFACTOR":
            assert isinstance(val, float)
            sp.priority_adjust_factor.priority_adjust_factor = val
        elif op == "ADJUSTTIME":
            assert isinstance(val, int)
            sp.priority_adjust_time.priority_adjust_time = val
        else:
            raise ProgrammingError(reason=f"Syntax error. Invalid SET {op}")

        return req

    def response(self) -> proto.ConfirmationResponse:
        """Generates a SET_PARAMETER response protobuf"""
        return proto.ConfirmationResponse()


class _CancelQueryFactory(_OcientRequestFactory[proto.CancelQueryResponse]):
    def request(self, id: str) -> proto.Request:
        """Generates a fully populated CANCEL QUERY request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("CANCEL_QUERY")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        req.cancel_query.sql = id
        return req

    def response(self) -> proto.CancelQueryResponse:
        """Generates a CANCEL_QUERY response protobuf"""
        return proto.CancelQueryResponse()


class _KillQueryFactory(_OcientRequestFactory[proto.KillQueryResponse]):
    def request(self, id: str) -> proto.Request:
        """Generates a fully populated KILL QUERY request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("KILL_QUERY")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        req.kill_query.sql = id
        return req

    def response(self) -> proto.KillQueryResponse:
        """Generates a KILL_QUERY response protobuf"""
        return proto.KillQueryResponse()


class _GetSystemMetadataFactory(_OcientRequestFactory[proto.FetchSystemMetadataResponse]):
    def request(self, op: proto.FetchSystemMetadata.SystemMetadataCall, schema: Optional[str], table: Optional[str], column: Optional[str], view: Optional[str]) -> proto.Request:  # type: ignore
        """Generates a fully populated GET_SYSTEM_METADATA request protobuf"""
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("FETCH_SYSTEM_METADATA")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
        req.fetch_system_metadata.call = op

        if schema is not None:
            req.fetch_system_metadata.schema = schema
        if table is not None:
            req.fetch_system_metadata.table = table
        if column is not None:
            req.fetch_system_metadata.column = column
        if view is not None:
            req.fetch_system_metadata.view = view

        return req

    def response(self) -> proto.FetchSystemMetadataResponse:
        """Generates a fully populated GET_SYSTEM_METADATA response protobuf"""
        return proto.FetchSystemMetadataResponse()


_OCIENT_REQUEST_FACTORIES: Mapping[str, _OcientRequestFactory[Any]] = {
    "SELECT": _ExecuteQueryFactory(),
    "WITH": _ExecuteQueryFactory(),
    "EXPLAIN PIPELINE": _ExplainPipelineFactory(),
    "EXPLAIN": _ExecuteExplainFactory(),
    "EXPORT": _ExecuteExportFactory(),
    "CHECK": _CheckDataFactory(),
    "FORCE": _ForceExternalFactory(),
    "SET SCHEMA": _SetSchemaFactory(),
    "GET SCHEMA": _GetSchemaFactory(),
    "CLEAR CACHE": _ClearCacheFactory(),
    "SET": _SetParameterFactory(),
    "CANCEL": _CancelQueryFactory(),
    "KILL": _KillQueryFactory(),
    "GET SYSTEM METADATA": _GetSystemMetadataFactory(),
    "SHOW": _ExecuteQueryFactory(),
}
"""Mapping from query type to its request factory"""


def _convert_exception(msg: proto.ConfirmationResponse) -> SQLException:
    """Internal routine to convert the google protobuf ConfirmationResponse
    to an exception
    """
    if msg.vendor_code < 0:
        return Error(sql_state=msg.sql_state, reason=msg.reason, vendor_code=msg.vendor_code)

    return Warning(sql_state=msg.sql_state, reason=msg.reason, vendor_code=msg.vendor_code)


def _send_msg(conn: "Connection", protobuf_msg: Message) -> None:
    """Internal routine to send a protobuf message on a connection"""
    if not conn.sock:
        raise ProgrammingError("Connection not available")

    logger.debug(f"Sending message on socket {conn.sock}: {protobuf_msg}")

    try:
        conn.sock.sendall(struct.pack("!i", protobuf_msg.ByteSize()) + protobuf_msg.SerializeToString())
    except IOError:
        raise IOError("Network send error")


def _recv_all(conn: "Connection", size: int) -> bytes:
    """Internal routine to receive `size` bytes of data from a connection"""
    if not conn.sock:
        raise Error("Connection not available")

    while len(conn._buffer) < size:
        received = conn.sock.recv(16777216)  # 16MB buffer
        if not received:
            raise IOError("Network receive error")
        conn._buffer += received

    ret = conn._buffer[:size]
    conn._buffer = conn._buffer[size:]

    return ret


def _recv_msg(conn: "Connection", protobuf_msg: _MsgT) -> _MsgT:
    """Internal routine to receive a protobuf message on a connection"""
    hdr = _recv_all(conn, 4)
    msgsize = _unpack_int(hdr)[0]

    msg = _recv_all(conn, msgsize)

    protobuf_msg.ParseFromString(msg)

    logger.debug(f"Received message on connection {conn.sock}: {protobuf_msg}")

    return protobuf_msg


def Date(year: int, month: int, day: int) -> datetime.datetime:  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct a
    Date object from year, month, day
    """
    return datetime.datetime(year, month, day)


def Time(hour: int, minute: int, second: int) -> datetime.time:  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct a
    Time object from hour, minute, second
    """
    return datetime.time(hour, minute, second)


def Timestamp(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> float:  # pylint: disable=invalid-name,too-many-arguments
    """Type constructor required in PEP 249 to construct
    a Timestamp object from year, month, day, hour, minute, second
    """
    return datetime.datetime(year, month, day, hour, minute, second).timestamp()


def DateFromTicks(ticks: float) -> datetime.datetime:  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct
    a Date object from a timestamp of seconds since epoch
    """
    return datetime.datetime.utcfromtimestamp(ticks)


def TimeFromTicks(ticks: float) -> datetime.time:  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct
    a Time object from a timestamp of seconds since epoch
    """
    date_time = datetime.datetime.utcfromtimestamp(ticks)
    return datetime.time(date_time.hour, date_time.minute, date_time.second)


def TimestampFromTicks(ticks: float) -> float:  # pylint: disable=invalid-name
    """Type constructor required in PEP 249 to construct
    a Timestamp object from a timestamp of seconds since epoch
    """
    return ticks


def _hash_key(shared_key: bytes, salt: bytes) -> bytes:
    """Internal key hash function"""
    # No idea where this algorithm came from, but do a home grown key
    # derivation function
    buffer = struct.pack("!i", len(shared_key))
    buffer = buffer + salt
    buffer = buffer + shared_key
    hasher = hashes.Hash(hashes.SHA256(), backend=default_backend())
    hasher.update(buffer)
    return hasher.finalize()


# Sessions code

# Used for representing a session created with a security token sign in


class SecurityToken:
    def __init__(self, tokenData: str, tokenSignature: str, issuerFingerprint: str) -> None:
        self.tokenData = tokenData
        self.tokenSignature = tokenSignature
        self.issuerFingerprint = issuerFingerprint


# Used for representing a session created with a user and password sign in.


class UserAndPassword:
    def __init__(self, user: str, password: str) -> None:
        self.user = user
        self.password = password


class Session:
    def __init__(
        self, securityToken: Optional[SecurityToken] = None, userAndPassword: Optional[UserAndPassword] = None
    ) -> None:
        # Only one of these should be instantiated. The other MUST be none.
        if (securityToken is None and userAndPassword is None) or (
            securityToken is not None and userAndPassword is not None
        ):
            raise ValueError("Exactly one of securityToken and userAndPassword must be specified")
        self.securityToken = securityToken
        self.userAndPassword = userAndPassword


class Connection:
    """A connection to the Ocient database. Normally constructed by
    calling the module `connect()` call, but can be constructed
    directly
    """

    # pylint: disable=too-many-instance-attributes
    TLS_NONE = 1  # : :meta private:
    TLS_UNVERIFIED = 2  # : :meta private:
    TLS_ON = 3  # : :meta private:

    HANDSHAKE_CBC = 1
    HANDSHAKE_GCM = 2
    HANDSHAKE_SSO = 3

    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 4050
    DEFAULT_DATABASE = "system"

    hosts: List[str] = []
    port = None
    database = None
    tls = None
    force = None
    handshake = None
    user = None
    password = None
    secondary_interfaces: Optional[List[List[Tuple[str, int]]]] = None
    secondary_index = -1
    sock: Optional[Union[socket.socket, ssl.SSLSocket]] = None
    session_id = str(uuid.uuid1())

    session = None
    serverSessionId = None

    # Whether the next execute query run on this connection will be redirected. Does nothing if force is set to true
    force_next_redirect = False

    # Sessions code end

    # the PEP 249 standard recommends making the module level exceptions
    # also attributes on the Connection class
    Error = Error
    Warning = Warning
    InterfaceError = InterfaceError
    DatabaseError = DatabaseError
    InternalError = InternalError
    OperationalError = OperationalError
    ProgrammingError = ProgrammingError
    IntegrityError = IntegrityError
    DataError = DataError
    NotSupportedError = NotSupportedError

    def _sslize_connection(self) -> None:
        """
        If SSL is specified, wrap the Connection's socket in an SSL connection
        """
        if self.tls != self.TLS_NONE:
            assert self.sock is not None
            logger.debug("Creating TLS connection")
            context = ssl.create_default_context()
            context.check_hostname = False
            if self.tls != self.TLS_ON:
                context.verify_mode = ssl.CERT_NONE
            self.sock = context.wrap_socket(self.sock)

    # Note that there are a couple of places in the code where we reconstruct the Connection.  If you add a parameter here, make sure to update those
    # places
    def __init__(
        self,
        dsn: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        database: Optional[str] = None,
        tls: Optional[Union[str, int]] = None,
        handshake: Optional[int] = None,
        force: Optional[bool] = None,
        configfile: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> None:
        # pylint: disable=too-many-arguments,no-member
        """Connection parameters can be specified as part of the dsn,
        using keyword arguments or both.  If both are specified, the keyword
        parameter overrides the value in the dsn.

        The Ocient DSN is of the format:
        `ocient://user:password@[host][:port][/database][?param1=value1&...]`

        `user` and `password` must be supplied.  `host` defaults to localhost,
        port defaults to 4050, database defaults to `system` and `tls` defaults
        to `off`.

        Multiple hosts may be specified, separated by a comma, in which case the
        hosts will be tried in order  Thus an example DSN might be
        `ocient://someone:somepassword@host1,host2:4051/mydb`

        configfile is the name of a configuration file in INI format, where each
        section is either default, or a pattern that matches the host and optionally
        database. sections are matched in order, so more specific sections should
        precede less specific sections::

            [DEFAULT]
            tls = unverified

            # This will match the specific host and database
            [foo.ocient.com/somedb]
            user = panther
            password = pink

            # This will match the specific host
            [foo.ocient.com]
            user = panther
            password = pink

            # This will match any host in the ocient.com domain
            [*.ocient.com]
            user = tom
            password = jerry
            database = mice

            # This will match any host in the ocient.com domain
            [*.ocient.com]
            user = tom
            password = jerry

        Currently supported parameters are:

        - tls: Which can have the values "off", "unverified", or "on" in the dsn,
            or Connection.TLS_NONE, Connection.TLS_UNVERIFIED, or
            Connection.TLS_ON as a keyword parameter.
        - force: True or False, whether to force the connection to remain on this
            server
        """
        # pylint: disable=no-member
        self._parse_args(dsn, user, password, host, database, tls, handshake, force, configfile)
        assert self.port is not None

        saved_exc: Optional[Exception] = None
        for one_host in self.hosts:
            try:
                logger.info(f"Trying to connect to {one_host}:{self.port}")
                self.sock = socket.create_connection((one_host, self.port))
                logger.info(f"Connected to {one_host}:{self.port} on socket {self.sock}")
                saved_exc = None
                break
            except ConnectionError as exc:
                saved_exc = exc
            except Exception as exc:
                saved_exc = exc

        if saved_exc is not None:
            raise Error(f"Unable to connect to {','.join(self.hosts)}:{self.port}: {str(saved_exc)}") from saved_exc

        self._sslize_connection()

        self._buffer: bytes = b""
        self.session = session
        if self.handshake == self.HANDSHAKE_SSO:
            if self.user or self.password:
                # If either are non-empty, use the CBC_GCM.
                self._client_handshake_CBC_GCM(is_explicit_sso=True, force=self.force)
            else:
                if self.session is not None and self.session.securityToken is not None:
                    self._client_handshake_security_token()
                else:
                    self._client_handshake_SSO()
        else:
            self._client_handshake_CBC_GCM(is_explicit_sso=False, force=self.force)

    def __enter__(self) -> "Connection":
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        pass

    def _initialize_client_connection(
        self,
        client_connection_message: Union[
            proto.ClientConnection,
            proto.ClientConnectionGCM,
            proto.ClientConnectionSecurityToken,
            proto.ClientConnectionSSO,
        ],
    ) -> None:
        """Initializes fields used in initial client handshake requests.
        1. database
        2. clientid (pyocient)
        3. protocol version
        4. version_major
        5. version_minor
        6. session id

        Note, not all fields are initialized. Some fields are special to certain client handshakes.
        For example, the SSO handshake with token does not take user and instead takes a security token.

        Args:
            client_connection_message ([proto message]): the client handshake request to initialize
        """
        assert self.database is not None
        client_connection_message.database = self.database
        client_connection_message.clientid = DRIVER_ID
        client_connection_message.version = PROTOCOL_VERSION
        client_connection_message.majorClientVersion = version_major
        client_connection_message.minorClientVersion = version_minor
        client_connection_message.sessionID = self.session_id

    def _client_handshake_CBC_GCM(self, is_explicit_sso: bool = False, force: bool = False) -> None:
        while True:
            ##################################################################
            # Send the CLIENT_CONNECTION request
            ##################################################################
            client_connection: Union[proto.ClientConnection, proto.ClientConnectionGCM]
            req = proto.Request()
            if self.handshake == self.HANDSHAKE_CBC:
                req.type = req.CLIENT_CONNECTION
                client_connection = req.client_connection
            else:
                # Should be GCM
                req.type = req.CLIENT_CONNECTION_GCM
                client_connection = req.client_connection_gcm
                client_connection.explicitSSO = is_explicit_sso
            assert self.user is not None
            client_connection.userid = self.user
            self._initialize_client_connection(client_connection)

            _send_msg(self, req)

            ##################################################################
            # Get the CLIENT_CONNECTION response and process it
            ##################################################################
            rsp1: Union[proto.ClientConnectionResponse, proto.ClientConnectionGCMResponse]
            if self.handshake == self.HANDSHAKE_CBC:
                # CBC
                rsp1 = _recv_msg(self, proto.ClientConnectionResponse())
            else:
                # GCM or explicit SSO
                rsp1 = _recv_msg(self, proto.ClientConnectionGCMResponse())

            if rsp1.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp1.response.reason)
            elif not rsp1.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                raise _convert_exception(rsp1.response)

            peer_key = load_pem_public_key(
                rsp1.pubKey.encode(encoding="UTF-8", errors="strict"),
                backend=default_backend(),
            )
            if not isinstance(peer_key, DHPublicKey):
                raise Error(f"Public key was not DHPublicKey, was: {type(peer_key)}")
            (cipher, generated_hmac, public_key) = self._encryption_routine(rsp1.iv, peer_key)

            ##################################################################
            # Send the CLIENT_CONNECTION2 request
            ##################################################################
            req = proto.Request()
            if self.handshake == self.HANDSHAKE_CBC:
                req.type = req.CLIENT_CONNECTION2
                req.client_connection2.cipher = cipher
                req.client_connection2.force = force
                req.client_connection2.hmac = generated_hmac
                req.client_connection2.pubKey = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                ).decode()
            else:
                req.type = req.CLIENT_CONNECTION_GCM2
                req.client_connection_gcm2.cipher = cipher
                req.client_connection_gcm2.force = force
                req.client_connection_gcm2.hmac = generated_hmac
                req.client_connection_gcm2.explicitSSO = is_explicit_sso
                req.client_connection_gcm2.pubKey = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                ).decode()

            _send_msg(self, req)

            ##################################################################
            # Get the CLIENT_CONNECTION response and process it
            ##################################################################
            rsp2: Union[proto.ClientConnection2Response, proto.ClientConnectionGCM2Response]
            if self.handshake == self.HANDSHAKE_CBC:
                # CBC
                rsp2 = _recv_msg(self, proto.ClientConnection2Response())
            else:
                # GCM or explicit SSO
                rsp2 = _recv_msg(self, proto.ClientConnectionGCM2Response())

            if rsp2.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp2.response.reason)
            elif rsp2.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                # Save the server session id
                self.serverSessionId = rsp2.serverSessionId
                self.session = Session(userAndPassword=UserAndPassword(self.user, self.password))
                logger.info(f"Connected to server session Id: {self.serverSessionId}")
                # Save secondary interfaces.
                self._save_secondary_interfaces(rsp2.secondary)

                # Redirect the connection
                if rsp2.redirect:
                    assert self.sock is not None
                    self.sock.close()
                    mapped_host, mapped_port = self.resolve_new_endpoint(rsp2.redirectHost, rsp2.redirectPort)
                    logger.debug(
                        f"Redirecting connection to {rsp2.redirectHost}:{rsp2.redirectPort}, which maps to {mapped_host}:{mapped_port}"
                    )
                    self.sock = socket.create_connection((mapped_host, mapped_port))
                    logger.info(f"Connected to {mapped_host}:{mapped_port} on socket {self.sock}")
                    self._sslize_connection()

                    return self._client_handshake_CBC_GCM(is_explicit_sso, True)

                break

            # there is something broken in our handshake...retry
            if rsp2.response.vendor_code == -202:
                logger.debug("Handshake error...retrying")
                continue

            raise _convert_exception(rsp2.response)

    def _client_handshake_SSO(self) -> None:
        """Internal routine for single sign on handshake (SSO).
        1. Driver requests to sign on via SSO.
        2. Server sends back an authentication URL.
        3. Driver launches URL in default browser (or prints the url to std out if not possible)
        4. User authenticates in browser.
        5. Driver continuously polls the database until login completes.
        6. Upon completion, server sends back a security token with which the driver can connect. (Used for redirecting / reconnecting)
        """
        from webbrowser import open_new

        req = proto.Request()
        req.type = req.CLIENT_CONNECTION_SSO
        client_connection = req.client_connection_sso

        self._initialize_client_connection(client_connection)
        # Send message
        _send_msg(self, req)
        # Receive response
        rsp = _recv_msg(self, proto.ClientConnectionSSOResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            raise _convert_exception(rsp.response)

        # Open browser for user to authenticate.
        if not open_new(rsp.authUrl):
            logger.info(
                "[pyocient] Could not open default browser with webbrowser library. Please authenticate at: "
                + rsp.authUrl
            )
            print(
                "[pyocient] Could not open default browser with webbrowser library. Please authenticate at: ",
                rsp.authUrl,
            )

        # Poll the database
        self._poll_database(rsp.requestId)

    def _poll_database(self, requestId: str) -> None:
        """Polls the database until we either receive an error or a successful login message.

        Args:
            requestId (String): the request ID associated with this login attempt.
        """

        req = proto.Request()
        req.type = req.CLIENT_CONNECTION_SSO2
        assert self.force is not None
        req.client_connection_sso2.force = self.force
        req.client_connection_sso2.requestId = requestId

        keepPolling = True
        waitFor = 0
        while keepPolling:
            sleep(waitFor)
            # Poll
            _send_msg(self, req)

            # Receive response
            rsp = _recv_msg(self, proto.ClientConnectionSSO2Response())

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp.response.reason)
            elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                raise _convert_exception(rsp.response)

            if rsp.HasField("pollingIntervalSeconds"):
                # Continue polling
                waitFor = rsp.pollingIntervalSeconds
                continue
            else:
                # Success
                waitFor = 0
                keepPolling = False

        self.serverSessionId = rsp.sessionInfo.serverSessionId
        logger.debug(f"Connected to server session Id: {self.serverSessionId}")
        received_token = rsp.sessionInfo.securityToken
        self.session = Session(
            securityToken=SecurityToken(
                received_token.data,
                received_token.signature,
                received_token.issuerFingerprint,
            )
        )

        # Save secondary interfaces.
        self._save_secondary_interfaces(rsp.secondary)

        # Redirect the connection
        if rsp.redirect:
            assert self.sock is not None
            self.sock.close()
            mapped_host, mapped_port = self.resolve_new_endpoint(rsp.redirectHost, rsp.redirectPort)
            logger.debug(
                f"Redirecting connection to {rsp.redirectHost}:{rsp.redirectPort}, which maps to {mapped_host}:{mapped_port}"
            )
            self.sock = socket.create_connection((mapped_host, mapped_port))
            logger.info(f"Connected to {mapped_host}:{mapped_port} on socket {self.sock}")
            self._sslize_connection()

            return self._client_handshake_security_token(True)

    def _client_handshake_security_token(self, force: bool = False) -> None:
        """Once a connection acquires a security token, it can use that to log in. This handshake only
        sends 1 message whereas the other handshakes send 2. self.session.securityToken must be set.
        """
        while True:
            req = proto.Request()
            req.type = req.CLIENT_CONNECTION_SECURITY_TOKEN
            client_connection = req.client_connection_security_token

            self._initialize_client_connection(client_connection)
            # Attach the security token used to log in
            assert self.session is not None
            assert self.session.securityToken is not None
            client_connection.securityToken = self.session.securityToken.tokenData
            client_connection.tokenSignature = self.session.securityToken.tokenSignature
            client_connection.issuerFingerprint = self.session.securityToken.issuerFingerprint
            client_connection.force = force

            _send_msg(self, req)

            rsp = _recv_msg(self, proto.ClientConnectionSecurityTokenResponse())

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp.response.reason)
            elif rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                # Save secondary interfaces.
                self._save_secondary_interfaces(rsp.secondary)
                # Redirect the connection if requested
                if rsp.redirect:
                    assert self.sock is not None
                    self.sock.close()
                    mapped_host, mapped_port = self.resolve_new_endpoint(rsp.redirectHost, rsp.redirectPort)
                    logger.debug(
                        f"Redirecting connection to {rsp.redirectHost}:{rsp.redirectPort}, which maps to {mapped_host}:{mapped_port}"
                    )
                    self.sock = socket.create_connection((mapped_host, mapped_port))
                    logger.info(f"Connected to {mapped_host}:{mapped_port} on socket {self.sock}")
                    self._sslize_connection()

                    return self._client_handshake_security_token(True)

                # Capture the session id
                self.serverSessionId = rsp.serverSessionId
                logger.debug(f"Connected to server session Id: {self.serverSessionId}")
                break
            # there is something broken in our handshake...retry
            if rsp.response.vendor_code == -202:
                logger.debug("Handshake error...retrying")
                continue

            raise _convert_exception(rsp.response)

    def _save_secondary_interfaces(
        self, new_secondary_interfaces: RepeatedCompositeFieldContainer[proto.SecondaryInterfaceList]
    ) -> None:
        """After secondary interfaces are sent from the server, we need to
        save them and use them for redirecting. This is important if we
        get redirected to mapped sql endpoints.

        Args:
            secondary_interfaces ([class 'google.protobuf.internal.containers.RepeatedCompositeContainer']):
            the secondary interfaces, which is really a list of list of strings.
        """
        self.secondary_interfaces = []
        for i in range(len(new_secondary_interfaces)):
            self.secondary_interfaces.append([])
            for j in range(len(new_secondary_interfaces[i].address)):
                interface = new_secondary_interfaces[i].address[j]
                (interface_ip, interface_port) = interface.split(":")
                # Return of gethostbyname_ex is (hostname, alias of host name, other ip addresses of host name)
                try:
                    other_ips = socket.gethostbyname_ex(interface_ip)[2]
                    for other_ip in other_ips:
                        self.secondary_interfaces[i].append((other_ip, int(interface_port)))
                except socket.gaierror:
                    pass

        hosts: List[Tuple[str, int]] = []
        assert self.port is not None
        for one_host in self.hosts:
            try:
                hosts = hosts + [(host, self.port) for host in socket.gethostbyname_ex(one_host)[2]]
            except socket.gaierror:
                pass
        for outer_list in self.secondary_interfaces:
            for index in range(len(outer_list)):
                if outer_list[index] in hosts:
                    self.secondary_index = index
                    break

        logger.debug(
            f"Saving secondary interfaces: index {self.secondary_index} interfaces: {self.secondary_interfaces}"
        )

    def _encryption_routine(
        self, initialization_vector: bytes, peer_key: DHPublicKey
    ) -> Tuple[bytes, bytes, DHPublicKey]:
        """Internal routine to do the encryption handshake of
        the password
        CBC is the previous form of encryption. We now use GCM by default.
        """
        # Create our keys using the parameters from the peer key
        params = peer_key.parameters()
        private_key = params.generate_private_key()

        # Create a shared key
        shared_key = private_key.exchange(peer_key)

        key = _hash_key(shared_key, b"\0")
        mac_key = _hash_key(shared_key, b"\1")

        assert self.password is not None
        if self.handshake == self.HANDSHAKE_CBC:
            # Pad the plaintext password out using PKCS7
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(self.password.encode(encoding="UTF-8", errors="strict"))
            padded_data += padder.finalize()

            # Encrypt the padded plaintext password using AES CBC and the key
            # we got from our KDF
            encryptor = Cipher(
                algorithms.AES(key),
                modes.CBC(initialization_vector),
                backend=default_backend(),
            ).encryptor()
            min_cipher_bytes = len(padded_data) + 4096
            buf = bytearray(min_cipher_bytes)
            len_encrypted = encryptor.update_into(padded_data, buf)
            cipher = bytes(buf[:len_encrypted]) + encryptor.finalize()
        else:
            encryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(initialization_vector),
                backend=default_backend(),
            ).encryptor()
            # We do not use AAD
            cipher = encryptor.update(self.password.encode(encoding="UTF-8", errors="strict")) + encryptor.finalize()
            # Server side expects that the tag is at the end of the cipher text.
            cipher += encryptor.tag

        # Now create an HMAC using the other KDF derived key and the
        # encrypted password
        hasher = hmac.HMAC(mac_key, hashes.SHA256(), backend=default_backend())
        hasher.update(cipher)
        generated_hmac = hasher.finalize()

        return (cipher, generated_hmac, private_key.public_key())

    def _parse_args(
        self,
        dsn: Optional[str],
        user: Optional[str],
        password: Optional[str],
        host: Optional[str],
        database: Optional[str],
        tls: Optional[Union[str, int]],
        handshake: Optional[int],
        force: Optional[bool],
        configfile: Optional[str],
    ) -> None:  # pylint: disable=too-many-arguments
        """Internal routine to resolve function arguments, config file, and dsn"""
        # pylint: disable=no-member,too-many-branches,too-many-statements
        # First, parse the DSN if it exists
        if dsn is not None:
            parsed = dsnparse.parse(dsn)

            if parsed.scheme and parsed.scheme.lower() != "ocient":
                raise MalformedURL(f"Invalid DSN scheme: {parsed.scheme}")

            for attr in ["database", "user", "password", "port"]:
                setattr(self, attr, getattr(parsed, attr))

            if parsed.host:
                self.hosts = parsed.host.split(",")

            if self.database is not None and len(self.database) == 0:
                self.database = None
            if self.database is not None and self.database[0] == "/":
                self.database = self.database[1:]

            if "tls" in parsed.query:
                self.tls = parsed.query["tls"]

            if "force" in parsed.query:
                shouldForce = parsed.query["force"]
                if shouldForce.upper() == "TRUE":
                    self.force = True
                elif shouldForce.upper() == "FALSE":
                    self.force = False
                else:
                    raise MalformedURL(f"Invalid force string: {shouldForce}")

            if force is not None:
                self.force = force

            if "handshake" in parsed.query:
                handshake = parsed.query["handshake"].lower()

            if self.user is None:
                self.user = ""

            if self.password is None:
                self.password = ""

        # Now override the DSN values with any values passed in as parameters
        if user is not None:
            self.user = user

        if password is not None:
            self.password = password

        if host:
            # Handle host:port
            parts = host.split(":")
            if len(parts) == 1:
                self.hosts = parts[0].split(",")
            elif len(parts) == 2:
                self.hosts = parts[0].split(",")
                self.port = int(parts[1])
            else:
                raise MalformedURL(f"Invalid host value: {host}")

        if database:
            self.database = database

        if tls is not None:
            self.tls = tls

        if handshake is not None:
            self.handshake = handshake

        # Set the default host now, since we use that as a key into the
        # config file
        if not self.hosts:
            self.hosts = [self.DEFAULT_HOST]

        # Now build a configparser with default values
        config = configparser.ConfigParser(
            defaults={
                "port": str(self.DEFAULT_PORT),
                "database": self.DEFAULT_DATABASE,
                "tls": "unverified",
                "force": "false",
                "handshake": "",
            },
            interpolation=None,
        )
        configvals = None

        # If we have a config file try loading that
        if configfile is not None:
            config.read(configfile)

            # Work out the host/database if we know it
            host_db = ",".join(self.hosts)
            if self.database is not None:
                host_db = host_db + "/" + self.database

            # Try and match each section in the INI file with the host/database
            for s in config.sections():
                if re.match(s, host_db):
                    configvals = config[s]
                    break

        # if we didn't find a matching host (or there is no file). use the defaults
        if configvals is None:
            configvals = config["DEFAULT"]
        # Force is not places here so it can get parsed below.
        for attr in ["port", "database", "tls", "handshake"]:
            if getattr(self, attr) is None:
                setattr(self, attr, configvals[attr])

        if not self.user:
            self.user = str(configvals.get("user", ""))

        if not self.password:
            self.password = str(configvals.get("password", ""))

        if self.force is None:
            self.force = configvals.getboolean("force")

        # And finally tidy up some things
        if isinstance(self.port, str):
            self.port = int(self.port)

        if isinstance(self.tls, str):
            if self.tls.lower() == "off":
                self.tls = self.TLS_NONE
            elif self.tls.lower() == "unverified":
                self.tls = self.TLS_UNVERIFIED
            elif self.tls.lower() == "on":
                self.tls = self.TLS_ON
            else:
                raise MalformedURL(f"Invalid tls value: {self.tls}")
        elif isinstance(self.tls, list):
            raise MalformedURL(f"Multiple TLS values detected: {self.tls}")

        if isinstance(self.handshake, str):
            if self.handshake.lower() == "cbc":
                self.handshake = self.HANDSHAKE_CBC
            elif self.handshake.lower() == "sso":
                self.handshake = self.HANDSHAKE_SSO
            # If they didn't specify handshake, it will be blank and thus should be GCM.
            elif self.handshake.lower() == "gcm" or self.handshake.lower() == "":
                self.handshake = self.HANDSHAKE_GCM
            else:
                print(self.handshake)
                raise MalformedURL(f"Invalid handshake value: {self.handshake}")

        # Don't assert a user parameter has been set. An empty
        # string for this field is used for authenticating SSO users

        # Don't assert a password parameter has been set. At empty
        # user and password is for authentication flow with SSO.

    def close(self) -> None:
        """Close the connection. Subsequent queries on this connection
        will fail
        """
        if not self.sock:
            raise Error("No connection")

        try:
            # Send end session message
            req = proto.Request()
            req.type = req.CLOSE_CONNECTION
            req.close_connection.endSession = True
            _send_msg(self, req)
        except IOError as e:
            # Ignore end session errors
            pass
        finally:
            logger.debug(f"Closing connection on socket {self.sock}")
            # Do this little dance so that even if the close() call
            # blows up, we have already set self.sock to None
            sock = self.sock
            self.sock = None
            sock.close()

    def commit(self) -> None:
        """Commit a transaction. Currently ignored"""

    def cursor(self) -> "Cursor":
        """Return a new cursor for this connection"""
        if not self.sock:
            raise Error("No connection")
        return Cursor(self)

    def __del__(self) -> None:
        if self.sock is not None:
            self.close()

    def resolve_new_endpoint(self, new_host: str, new_port: int) -> Tuple[str, int]:
        """
        Handles mapping to a secondary interface based on the secondary interface mapping saved on this connection.

        Args:
            new_host[string]: the new host to be remapped
            new_port[int]: the new port to be remapped

        Returns:
            [tuple(string, int)]: The actual endpoint to connect to in the format: (host, port).
        """
        logger.debug(
            f"Resolving new endpoint {new_host}:{new_port} with secondary_index {self.secondary_index} and secondary_interface {self.secondary_interfaces}"
        )

        new_endpoint = (new_host, new_port)
        endpoint_to_connect = None
        if self.secondary_index != -1:
            assert self.secondary_interfaces is not None
            outer_index = 0
            for outer_list in self.secondary_interfaces:
                if outer_list[0] == new_endpoint:
                    break
                outer_index += 1
            if outer_index < len(self.secondary_interfaces):
                endpoint_to_connect = self.secondary_interfaces[outer_index][self.secondary_index]
            else:
                endpoint_to_connect = new_endpoint

        else:
            endpoint_to_connect = new_endpoint

        logger.debug(f"Resolved new endpoint {new_host}:{new_port} to {endpoint_to_connect}")

        return endpoint_to_connect

    def redirect(self, new_host: str, new_port: int) -> "Connection":
        """
        Redirects to the proper secondary interface given a new endpoint.

        Args:
            new_host[string]: the new host to be remapped
            new_port[int]: the new port to be remapped

        Returns:
            [Connection]: A new connection.
        """
        remapped_host, remapped_port = self.resolve_new_endpoint(new_host, new_port)
        new_endpoint = f"{remapped_host}:{remapped_port}"
        logger.debug(f"Redirecting connection to {new_host}:{new_port}, which maps to {remapped_host}:{remapped_port}")

        return Connection(
            user=self.user,
            password=self.password,
            host=new_endpoint,
            database=self.database,
            tls=self.tls,
            handshake=self.handshake,
            force=self.force,
            session=self.session,
        )

    def refresh(self) -> None:
        """
        Used to refresh the session associated with this connection. The server will
        return a new server session id and security token.
        """
        req = proto.Request()
        req.type = req.CLIENT_CONNECTION_REFRESH_SESSION

        # Send message
        _send_msg(self, req)
        # Receive message
        rsp = _recv_msg(self, proto.ClientConnectionRefreshSessionResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            # Capture the session id
            self.serverSessionId = rsp.sessionInfo.serverSessionId
            logger.debug(f"Connected to server session Id: {self.serverSessionId}")
            received_token = rsp.sessionInfo.securityToken
            if self.session is not None and self.session.securityToken is not None:
                self.session = Session(
                    securityToken=SecurityToken(
                        received_token.data,
                        received_token.signature,
                        received_token.issuerFingerprint,
                    )
                )
            else:
                # Ignore the security token
                assert self.user is not None
                assert self.password is not None
                self.session = Session(userAndPassword=UserAndPassword(self.user, self.password))
            return
        # Something bad happened with the refresh attempt.
        raise _convert_exception(rsp.response)


class Cursor:
    # pylint: disable=too-many-instance-attributes
    """A database cursor, which is used to manage a query and its returned results"""

    def __init__(self, conn: Connection) -> None:
        """Cursors are normally created by the cursor() call on a connection, but can
        be created directly by providing a connection
        """
        self.connection = conn
        self.arraysize = 1

        self._reinitialize()

    def __del__(self) -> None:
        try:
            self._close_resultset()
        except Exception:
            pass

    def __enter__(self) -> "Cursor":
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
    ) -> None:
        pass

    def _reinitialize(self) -> None:
        """Internal function to initialize a cursor"""
        # Set the state
        self.query_id = None
        self.rowcount = -1
        self.rownumber: Optional[int] = None
        self.resultset_tuple: Optional[Type[NamedTuple]] = None
        self.description: Optional[List[Tuple[str, int, None, None, None, None, None]]] = None
        self.end_of_data = False
        self.generated_result: Optional[str] = None
        self.list_result: Optional[List[NamedTuple]] = None
        self._buffers: List[bytes] = []
        self._offset = 0
        self._pending_ops: List[str] = []

    def setinputsizes(self, sizes: Sequence[Optional[int]]) -> None:
        """This can be used before a call to .execute*() to predefine
        memory areas for the operation's parameters. Currently ignored
        """

    def setoutputsize(self, size: int, column: Optional[int] = None) -> None:
        """Set a column buffer size for fetches of large columns
        (e.g. LONGs, BLOBs, etc.). The column is specified as an
        index into the result sequence. Currently ignored
        """

    def close(self) -> None:
        """Close this cursor.  The current result set is closed, but
        the cursor can be reused for subsequent execute() calls.
        """
        if self._buffers:
            try:
                self._close_resultset()
            except Exception:
                pass

        self._reinitialize()

    def executemany(
        self, operation: Union[str, bytes], parameterlist: Iterable[Mapping[Union[str, bytes], object]]
    ) -> "Cursor":
        """Prepare a database operation (query or command) and then execute it against
        all parameter sequences or mappings found in the sequence parameterlist.

        Parameters may be provided as a mapping and will be bound to variables
        in the operation. Variables are specified in Python extended format codes,
        e.g. ...WHERE name=%(name)s
        """
        self._reinitialize()

        if isinstance(operation, bytes):
            operation = operation.decode()

        # we can't just execute all the queries at once....ocient only allows
        # one query at a time on a connection.  So queue up all the queries and
        # we'll call them later
        for param in parameterlist:
            param = {key.decode() if isinstance(key, bytes) else key: value for (key, value) in param.items()}
            self._pending_ops.append(operation % param)

        if self._pending_ops:
            self._execute_internal(self._pending_ops.pop(0))

        return self

    def execute(self, operation: Union[str, bytes], parameters: Mapping[Union[str, bytes], object] = {}) -> "Cursor":
        """Prepare and execute a database operation (query or command).

        Parameters may be provided as a mapping and will be bound to variables
        in the operation. Variables are specified in Python extended format codes,
        e.g. ...WHERE name=%(name)s
        """
        self._reinitialize()

        if isinstance(operation, bytes):
            operation = operation.decode()

        params = {key.decode() if isinstance(key, bytes) else key: value for (key, value) in parameters.items()}

        self._execute_internal(operation, params)

        return self

    def _execute_internal(self, operation: str, parameters: Mapping[str, object] = {}) -> None:
        """Internal execute routine that gets called from execute and executemany"""
        # pylint: disable=too-many-branches

        # Expand format string
        if parameters:
            operation = operation % parameters

        # We need to figure out whether we should call
        # execute_query or execute_update
        stripped = operation

        # Loop until we have some starting words. Note this
        # doesn't actually handle the case of 'word1 /* comment */ word2',
        # but none of the other clients do either...
        while True:
            # strip off starting spaces
            stripped = stripped.lstrip()

            # if this starts with --, strip the rest of the line
            if stripped.startswith("--"):
                pos = stripped.find("\n")
                if pos == -1:
                    stripped = ""
                else:
                    stripped = stripped[pos + 1 :]

            # if this starts with /*, strip until */
            elif stripped.startswith("/*"):
                pos = stripped.find("*/")
                if pos == -1:
                    stripped = ""
                else:
                    stripped = stripped[pos + 2 :]
            else:
                # yay, no comments, move to the next phase
                break

        # if we don't have anything left, just return []
        if not stripped:
            return

        # now split out the words
        words = stripped.split(None, 3)

        # Single word matches
        query_type = words[0].upper()
        if query_type in ["SELECT", "WITH", "EXPORT", "CHECK", "SHOW"]:
            return self._execute_query(operation=operation, query_type=query_type)
        elif query_type in ["EXPLAIN"]:
            # explain pipeline
            if len(words) > 1 and words[1].upper() == "PIPELINE":
                return self._execute_query(operation=operation, query_type=query_type + " PIPELINE")
            else:
                return self._execute_query(operation=operation, query_type=query_type)
        elif query_type in ["LIST"]:
            if operation.upper() == "LIST ALL QUERIES":
                return self._execute_query(operation="SELECT * FROM SYS.QUERIES", query_type="SELECT")
            elif operation.upper() == "LIST ALL COMPLETED QUERIES":
                return self._execute_query(operation="SELECT * FROM SYS.COMPLETED_QUERIES", query_type="SELECT")
            else:
                return self._execute_list(operation=operation)
        elif query_type == "FORCE":
            self._execute_force(operation=operation)
        elif query_type == "SET":
            self._execute_set(words[1:])
        elif query_type == "GET":
            self._execute_get(words[1:])
        elif query_type == "KILL":
            self._execute_cancelkill(query_type, words[1:])
        elif query_type == "CANCEL":
            if len(words) > 1 and words[1].upper() == "TASK":
                self._execute_update(operation)
            else:
                self._execute_cancelkill(query_type, words[1:])
        elif query_type == "CLEAR":
            self._execute_clear(words[1:])
        else:
            # ok, this is an update
            self._execute_update(operation)

    def tables(self, schema: str = "%", table: str = "%") -> "Cursor":
        """Get the database tables"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_TABLES, schema=schema, table=table)
        return self

    def system_tables(self, table: str = "%") -> "Cursor":
        """Get the database system tables"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_SYSTEM_TABLES, table=table)
        return self

    def views(self, view: str = "%") -> "Cursor":
        """Get the database views"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_VIEWS, view=view)
        return self

    def columns(self, schema: str = "%", table: str = "%", column: str = "%") -> "Cursor":
        """Get the database columns"""
        # pylint: disable=no-member
        self._metadata_req(
            proto.FetchSystemMetadata.GET_COLUMNS,
            schema=schema,
            table=table,
            column=column,
        )
        return self

    def indexes(self, schema: str = "%", table: str = "%") -> "Cursor":
        """Get the database indexes"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_INDEX_INFO, schema=schema, table=table)
        return self

    def getTypeInfo(self) -> "Cursor":  # pylint: disable=invalid-name
        """Get the database type info"""
        # pylint: disable=no-member
        self._metadata_req(proto.FetchSystemMetadata.GET_TYPE_INFO)
        return self

    def getSystemVersion(self) -> Union[int, str, None]:
        return self._execute_systemmetadata(proto.FetchSystemMetadata.GET_DATABASE_PRODUCT_VERSION)

    def _metadata_req(
        self,
        reqtype: proto.FetchSystemMetadata.SystemMetadataCall,
        schema: str = "%",
        table: str = "%",
        column: str = "%",
        view: str = "%",
    ) -> None:
        """Internal function to get database metadata"""
        # pylint: disable=no-member,too-many-arguments
        self._reinitialize()
        # req.fetch_system_metadata.GET_TABLES
        req = proto.Request()
        req.type = req.FETCH_SYSTEM_METADATA
        req.fetch_system_metadata.call = reqtype
        req.fetch_system_metadata.schema = schema
        req.fetch_system_metadata.table = table
        req.fetch_system_metadata.column = column
        req.fetch_system_metadata.view = view
        req.fetch_system_metadata.test = True

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.FetchSystemMetadataResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_ERROR:
            if rsp.response.vendor_code == SESSION_EXPIRED_CODE:
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._metadata_req(reqtype, schema=schema, table=table, column=column, view=view)
                return
            else:
                raise _convert_exception(rsp.response)

        self._get_result_metadata()

        self.rownumber = 0
        for blob in rsp.result_set_val.blobs:
            if not self._buffers:
                self._offset = 0
            self._buffers.append(blob)

    def _execute_query(self, operation: str, query_type: str = "SELECT") -> None:
        """Execute a query"""
        # pylint: disable=no-member

        factory = _OCIENT_REQUEST_FACTORIES.get(query_type.upper(), None)

        if factory is None:
            raise NotSupportedError(f"Query type '{query_type}' not supported by pyocient'")

        # generate the appropriate request
        req = factory.request(operation)

        # Loop while we retry redirects and reconnects
        while True:
            assert self.connection.force is not None
            if req.type == proto.Request.RequestType.Value("EXECUTE_QUERY"):  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
                req.execute_query.force = self.connection.force
                req.execute_query.forceRedirect = self.connection.force_next_redirect
                self.connection.force_next_redirect = False
            elif req.type == proto.Request.RequestType.Value("EXECUTE_EXPLAIN"):  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240
                req.execute_explain.force = self.connection.force
            try:
                _send_msg(self.connection, req)

                rsp = _recv_msg(self.connection, factory.response())
            except IOError:
                # remake our connection
                self.connection = Connection(
                    user=self.connection.user,
                    password=self.connection.password,
                    host=f"{','.join(self.connection.hosts)}:{self.connection.port}",
                    database=self.connection.database,
                    tls=self.connection.tls,
                    handshake=self.connection.handshake,
                    force=self.connection.force,
                    session=self.connection.session,
                )

                continue

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp.response.reason)
            elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                if rsp.response.vendor_code == SESSION_EXPIRED_CODE:
                    # Need to refresh the session
                    self.connection.refresh()
                    # and try again
                    continue
                else:
                    raise _convert_exception(rsp.response)

            # see if we are being told to redirect
            redirect = getattr(rsp, "redirect", False)
            if not redirect:
                break

            # remake our connection
            self.connection.close()
            self.connection = self.connection.redirect(rsp.redirectHost, rsp.redirectPort)

        query_id = getattr(rsp, "queryId", None)
        if query_id is not None:
            self.query_id = query_id

        self.rownumber = 0

        if query_type in ["SELECT", "WITH", "SHOW"]:
            self._get_result_metadata()

        elif query_type == "EXPORT":
            self.description = [
                ("export", TypeCodes.CHAR, None, None, None, None, None)
            ]  # display_size  # internal_size  # precision  # scale  # null_ok
            self.resultset_tuple = namedtuple("Row", ("export",))  # type: ignore
            self.generated_result = rsp.exportStatement
        elif query_type == "EXPLAIN":
            self.description = [
                ("explain", TypeCodes.CHAR, None, None, None, None, None)
            ]  # display_size  # internal_size  # precision  # scale  # null_ok
            self.resultset_tuple = namedtuple("Row", ("explain",))  # type: ignore
            self.generated_result = rsp.plan
        elif query_type == "EXPLAIN PIPELINE":
            self.description = [
                ("explain_pipeline", TypeCodes.CHAR, None, None, None, None, None)
            ]  # display_size  # internal_size  # precision  # scale  # null_ok
            self.resultset_tuple = namedtuple("Row", ("explain_pipeline",))  # type: ignore
            self.generated_result = rsp.pipelineStatement
        elif query_type == "CHECK":
            # The result of the CHECK DATA statement is a string with a lot of linefeeds. TODO convert it to something reasonable
            self.description = [
                ("result", TypeCodes.CHAR, None, None, None, None, None),
            ]  # display_size  # internal_size  # precision  # scale  # null_ok
            self.resultset_tuple = namedtuple("Row", ("result",))  # type: ignore
            self.generated_result = rsp.checkDataStatement

    # After list all queries and list all completed queries have been remapped, this is no longer used. But it can be used for other things.
    # Ex: list tables, list views, list table privileges. None of these are implemented yet.
    def _execute_list(self, operation: str = "LIST ALL QUERIES") -> None:
        """Execute LIST_ALL_QUERIES"""
        # pylint: disable=no-member

        factory = _OCIENT_REQUEST_FACTORIES.get(operation.upper(), None)

        if factory is None:
            raise NotSupportedError(f"List query '{operation}' not supported by pyocient'")

        # geerate the appropriate request
        req = factory.request(operation)

        while True:
            try:
                _send_msg(self.connection, req)

                rsp = _recv_msg(self.connection, factory.response())
            except IOError:
                # remake our connection
                self.connection = Connection(
                    user=self.connection.user,
                    password=self.connection.password,
                    host=f"{','.join(self.connection.hosts)}:{self.connection.port}",
                    database=self.connection.database,
                    tls=self.connection.tls,
                    handshake=self.connection.handshake,
                    force=self.connection.force,
                    session=self.connection.session,
                )

                continue
            break

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            if rsp.response.vendor_code == SESSION_EXPIRED_CODE:
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_list(operation=operation)
                return
            else:
                raise _convert_exception(rsp.response)

        self.description = []

        rows = factory.process(rsp)
        if not rows:
            self.list_result = []
            return

        # Create the column descriptions
        row = rows[0]
        for field in row._fields:
            self.description.append(
                (
                    field,
                    TypeCodes.cls_to_type(row._field_types[field]),
                    None,
                    None,
                    None,
                    None,
                    None,
                )  # display_size  # internal_size  # precision  # scale  # null_ok
            )

        # and set the results
        self.list_result = rows

    def _get_result_metadata(self) -> None:
        """Internal routine to get metadata for a result set"""
        # pylint: disable=no-member
        req = proto.Request()
        req.type = req.FETCH_METADATA

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.FetchMetadataResponse())
        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            raise _convert_exception(rsp.response)

        cols = {}
        for key, value in rsp.cols2pos.items():
            cols[value] = key

        self.description = []
        colnames = []
        for i in range(len(cols)):  # pylint: disable=consider-using-enumerate
            name = cols[i]
            # This tuple is defined in PEP 249
            self.description.append(
                (
                    name,
                    TypeCodes.to_type(rsp.cols2Types[name]),
                    None,
                    None,
                    None,
                    None,
                    None,
                )
            )  # display_size  # internal_size  # precision  # scale  # null_ok
            colnames.append(name)
        self.resultset_tuple = namedtuple("Row", colnames, rename=True)  # type: ignore

    def _execute_update(self, operation: str) -> None:
        """Execute an update statement"""
        # pylint: disable=no-member
        # While we are redirecting...

        # There is no resultset data from an update
        self.end_of_data = True

        while True:
            req = proto.Request()
            req.type = req.EXECUTE_UPDATE
            req.execute_update.sql = operation
            assert self.connection.force is not None
            req.execute_update.force = self.connection.force

            try:
                _send_msg(self.connection, req)

                rsp = _recv_msg(self.connection, proto.ExecuteUpdateResponse())
            except IOError:
                # remake our connection
                self.connection = Connection(
                    user=self.connection.user,
                    password=self.connection.password,
                    host=f"{','.join(self.connection.hosts)}:{self.connection.port}",
                    database=self.connection.database,
                    tls=self.connection.tls,
                    handshake=self.connection.handshake,
                    force=self.connection.force,
                    session=self.connection.session,
                )

                continue

            if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
                warn(rsp.response.reason)
            elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
                if rsp.response.vendor_code == SESSION_EXPIRED_CODE:
                    # Need to refresh the session
                    self.connection.refresh()
                    # and try again
                    continue
                else:
                    raise _convert_exception(rsp.response)

            # see if we are being told to redirect
            if not rsp.redirect:
                self.rowcount = rsp.updateRowCount
                break

            # remake our connection
            self.connection = self.connection.redirect(rsp.redirectHost, rsp.redirectPort)

    def _execute_force(self, operation: str) -> None:
        if operation.strip().upper() == "FORCE REDIRECT":
            # Sets the next command that is execute query to redirect
            self.connection.force_next_redirect = True
            self.end_of_data = True
        else:
            # Force external command
            self._execute_force_external(operation)

    def _execute_force_external(self, operation: str) -> None:
        # pylint: disable=no-member
        # While we are redirecting...
        factory = _OCIENT_REQUEST_FACTORIES["FORCE"]
        req = factory.request(operation=operation)

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.ConfirmationResponse())

        if rsp.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.reason)
        elif not rsp.type == proto.ConfirmationResponse.RESPONSE_OK:
            raise _convert_exception(rsp)

    def _execute_set(self, params: Sequence[str]) -> None:
        if len(params) != 2:
            raise ProgrammingError(reason="Syntax error")

        # There is no resultset data from an update
        self.end_of_data = True

        op = params[0].upper()
        val: Union[int, str, float]
        val = params[1].strip()

        factory: Union[_SetSchemaFactory, _SetParameterFactory]
        if op == "SCHEMA":
            factory = _SetSchemaFactory()
            req = factory.request(val)
        elif op == "SERVICECLASS":  # Service Classes take string parameters, not int
            factory = _SetParameterFactory()
            req = factory.request(op, val)
        elif op == "PSO":
            # PSO supports 'on' and 'off' instead of 'reset'. 'on' is equivalent, and 'off' disables (equivalent to a negative value)
            val = val.lower()
            if val == "on":
                val = "reset"
            elif val == "off":
                val = -1
            else:
                try:
                    val = int(val)
                except ValueError:
                    raise ProgrammingError(reason="Syntax error in SET. Value must be numeric, 'on', or 'off'")
            factory = _SetParameterFactory()
            req = factory.request(op, val)
        elif op in ["ADJUSTFACTOR", "PRIORITY"]:
            if val.lower() != "reset":
                try:
                    val = float(val)
                except ValueError:
                    raise ProgrammingError(reason="Syntax error in SET. Value must be numeric or 'reset'")
            factory = _SetParameterFactory()
            req = factory.request(op, val)
        else:
            if val.lower() != "reset":
                try:
                    val = int(val)
                except ValueError:
                    raise ProgrammingError(reason="Syntax error in SET. Value must be numeric or 'reset'")
            factory = _SetParameterFactory()
            req = factory.request(op, val)

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.reason)
        elif not rsp.type == proto.ConfirmationResponse.RESPONSE_OK:
            if rsp.vendor_code == SESSION_EXPIRED_CODE:
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_set(params)
                return
            else:
                raise _convert_exception(rsp)

    def _execute_get_schema(self) -> None:
        factory = _GetSchemaFactory()
        req = factory.request()

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            if rsp.response.vendor_code == SESSION_EXPIRED_CODE:
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_get_schema()
                return
            else:
                raise _convert_exception(rsp.response)

        self.description = [
            ("schema", TypeCodes.CHAR, None, None, None, None, None)
        ]  # display_size  # internal_size  # precision  # scale  # null_ok

        Row = namedtuple("Row", ("schema",))
        self.list_result = [Row._make((rsp.schema,))]

    # If we need to implement more of these sorts of custom commands, consider
    # making a factory for the description and results.
    def _execute_get_server_session_id(self) -> None:
        if self.connection.serverSessionId is None:
            raise Error(reason=f"Connection {self.connection} for cursor {self} has no serverSessionId")
        self.description = [
            ("server_session_id", TypeCodes.CHAR, None, None, None, None, None)
        ]  # display_size  # internal_size  # precision  # scale  # null_ok
        Row = namedtuple("Row", ("server_session_id",))
        self.list_result = [Row._make((self.connection.serverSessionId,))]

    def _execute_get(self, params: Sequence[str]) -> None:
        if len(params) == 1 and params[0].upper() == "SCHEMA":
            self._execute_get_schema()
        elif (
            len(params) == 3
            and params[0].upper() == "SERVER"
            and params[1].upper() == "SESSION"
            and params[2].upper() == "ID"
        ):
            self._execute_get_server_session_id()
        else:
            raise ProgrammingError(reason="Syntax error")

    def _execute_clear(self, params: Sequence[str]) -> None:
        if len(params) != 1 or params[0].upper() != "CACHE":
            raise ProgrammingError(reason="Syntax error")

        # There is no resultset data from an update
        self.end_of_data = True

        factory = _ClearCacheFactory()
        req = factory.request()

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.reason)
        elif not rsp.type == proto.ConfirmationResponse.RESPONSE_OK:
            if rsp.vendor_code == SESSION_EXPIRED_CODE:
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_clear(params)
                return
            else:
                raise _convert_exception(rsp)

    def _execute_cancelkill(self, op: str, id: Sequence[str]) -> None:
        if len(id) != 1:
            raise ProgrammingError(reason="Syntax error")

        # There is no resultset data from an update
        self.end_of_data = True

        factory = _OCIENT_REQUEST_FACTORIES[op]
        req = factory.request(id[0])

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            if rsp.response.vendor_code == SESSION_EXPIRED_CODE:
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                self._execute_cancelkill(op, id)
                return
            else:
                raise _convert_exception(rsp.response)

    # TODO: replace the other metadata call
    def _execute_systemmetadata(
        self,
        op: proto.FetchSystemMetadata.SystemMetadataCall,
        schema: Optional[str] = None,
        table: Optional[str] = None,
        column: Optional[str] = None,
        view: Optional[str] = None,
    ) -> Union[int, str, None]:
        factory = _GetSystemMetadataFactory()
        req = factory.request(op, schema, table, column, view)

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, factory.response())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.response.reason)
        elif not rsp.response.type == proto.ConfirmationResponse.RESPONSE_OK:
            if rsp.response.vendor_code == SESSION_EXPIRED_CODE:
                # Need to refresh the session
                self.connection.refresh()
                # and try again
                return self._execute_systemmetadata(op, schema=schema, table=table, column=column, view=view)
            else:
                raise _convert_exception(rsp.response)

        if rsp.HasField("result_set_val"):
            self._get_result_metadata()

            for blob in rsp.result_set_val.blobs:
                self._buffers.append(blob)
            return None

        if rsp.HasField("string_val"):
            return rsp.string_val

        return rsp.int_val

    def _get_more_data(self) -> None:
        """Internal routine to get more data from a query"""
        # pylint: disable=no-member
        req = proto.Request()
        req.type = req.FETCH_DATA
        req.fetch_data.fetch_size = self.arraysize
        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.FetchDataResponse())

        if rsp.response.type == proto.ConfirmationResponse.RESPONSE_ERROR:
            raise _convert_exception(rsp.response)

        for blob in rsp.result_set.blobs:
            if not self._buffers:
                self._offset = 0
            self._buffers.append(blob)

    def fetchmany(self, size: Optional[int] = None) -> List[NamedTuple]:
        """Fetch the next set of rows of a query result, returning a sequence of
        sequences (e.g. a list of tuples). An empty sequence is returned when no
        more rows are available.

        The number of rows to fetch per call is specified by the parameter. If it
        is not given, the cursor's arraysize determines the number of rows to be
        fetched. The method will try to fetch as many rows as indicated by the size
        parameter. If this is not possible due to the specified number of rows not
        being available, fewer rows may be returned.
        """
        if size is None:
            size = self.arraysize

        rows: List[NamedTuple] = []
        while size > 0:
            a_row = self.fetchone()
            if a_row is None:
                break
            rows.append(a_row)
            size -= 1
        return rows

    def fetchall(self) -> List[NamedTuple]:
        """Fetch all (remaining) rows of a query result, returning them as a
        sequence of sequences (e.g. a list of tuples). Note that the cursor's
        arraysize attribute can affect the performance of this operation.
        """
        return self.fetchmany(size=sys.maxsize)

    def __next__(self) -> NamedTuple:
        a_row = self.fetchone()
        if a_row is None:
            raise StopIteration
        return a_row

    def __iter__(self) -> "Cursor":
        return self

    def fetchval(self) -> Optional[object]:
        """The fetchval() convenience method returns the first column of the
        first row if there are results, otherwise it returns None.
        """
        arow = self.fetchone()
        if arow:
            return cast(object, arow[0])
        return None

    def fetchone(self) -> Optional[NamedTuple]:
        """Fetch the next row of a query result set, returning a single sequence,
        or None when no more data is available.
        """
        # If there was never a query executed, throw an error
        if self.description is None:
            raise ProgrammingError("No result set available")

        # pylint: disable = too-many-branches
        if self.end_of_data:
            return None

        # special case explain.
        if self.generated_result is not None:
            self.end_of_data = True
            assert self.resultset_tuple is not None
            return self.resultset_tuple._make((self.generated_result,))

        if self.list_result is not None:
            if self._offset >= len(self.list_result):
                self.end_of_data = True
                return None
            a_row = self.list_result[self._offset]
            self._offset += 1
            return a_row

        if self.rowcount < 0:
            self.rowcount = 0

        while not self._buffers:
            self._get_more_data()
            while self._buffers and self._buf() == b"\0\0\0\0":
                self._buffers.pop(0)

            if not self._buffers:
                # no data yet...wait so we don't hammer the host before asking for more
                sleep(0.25)

        if self._offset == 0:
            self._get_num_rows()

        row_length = self._get_int() - 4  # row_length includes the 4 bytes we just consumed
        end_offset = self._offset + row_length

        if self._bytes_remaining() == 1 and self._buf()[self._offset] == TypeCodes.DEM:
            self.rowcount -= 1
            self._buffers.pop(0)
            self._close_resultset()
            return self._process_pending()

        tmp_row: List[object] = []
        while self._offset < end_offset:
            tmp_row.append(self._decode_entry())

        if self._offset >= len(self._buf()):
            self._buffers.pop(0)
            self._offset = 0
        assert self.rownumber is not None
        self.rownumber += 1
        assert self.resultset_tuple is not None
        return self.resultset_tuple._make(tmp_row)

    def _process_pending(self) -> Optional[NamedTuple]:
        # if we have any pending queries to execute, kick one off now
        if self._pending_ops:
            self._buffers = []
            self._offset = 0
            self._execute_internal(self._pending_ops.pop(0))
            return self.fetchone()

        self.end_of_data = True
        return None

    def _buf(self) -> bytes:
        return self._buffers[0]

    def _bytes_remaining(self) -> int:
        if not self._buffers:
            return 0
        return len(self._buffers[0]) - self._offset

    def _get_num_rows(self) -> None:
        if self._bytes_remaining() >= 4:
            self.rowcount += self._get_int()

    def _decode_entry(self) -> object:
        # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
        coltype = self._get_byte()

        # if this is the easy conversion, just do it
        if coltype in _type_map:
            tm = _type_map[coltype]
            return self._get_type(tm[0], tm[1])

        if coltype == TypeCodes.STRING:
            strlen = self._get_int()
            offset = self._offset
            self._offset += strlen
            return self._buf()[offset : offset + strlen].decode("utf-8", errors="replace")

        if coltype == TypeCodes.TIMESTAMP:
            return datetime.datetime.utcfromtimestamp(self._get_long())

        if coltype == TypeCodes.NULL:
            return None

        if coltype == TypeCodes.BYTE:
            return int.from_bytes(self._get_type(1, _unpack_char), "big", signed=True)

        if coltype == TypeCodes.TIME:
            long_seconds = self._get_long()
            second = long_seconds % 60
            minutes = long_seconds / 60
            minute = int(minutes % 60)
            hours = minutes / 60
            hour = int(hours % 24)
            return datetime.time(hour, minute, second)

        if coltype == TypeCodes.BINARY:
            strlen = self._get_int()
            offset = self._offset
            self._offset += strlen
            return self._buf()[offset : offset + strlen]

        if coltype == TypeCodes.DECIMAL:
            precision = self._get_byte()
            scale = self._get_byte()

            if precision % 2 == 0:
                strlen = int((precision / 2) + 1)
            else:
                strlen = int((precision + 1) / 2)

            data = self._buf()[self._offset : (self._offset + strlen - 1)]
            digits = []
            for byte in data:
                digits.append((byte & 0xF0) >> 4)
                digits.append(byte & 0x0F)

            sign = self._buf()[self._offset + strlen - 1]

            digits.append(sign >> 4)
            sign = sign & 0x0F

            if sign == 12:
                sign = 0
            elif sign == 13:
                sign = 1
            else:
                raise Error(reason=f"Unknown decimal sign value {sign}")

            self._offset += strlen
            return decimal.Decimal((sign, digits, -scale))

        if coltype == TypeCodes.ARRAY:
            nested_level = 0

            arraytype = self._get_byte()

            while arraytype == TypeCodes.ARRAY:
                arraytype = self._get_byte()
                nested_level += 1

            return self._get_array(nested_level)

        if coltype == TypeCodes.UUID:
            self._offset += 16
            return uuid.UUID(bytes=self._buf()[self._offset - 16 : self._offset])

        if coltype == TypeCodes.ST_POINT:
            long = self._get_double()
            lat = self._get_double()
            return _STPoint(long, lat)

        if coltype == TypeCodes.DATE:
            d = datetime.datetime.utcfromtimestamp(self._get_long() / 1000.0)
            return datetime.date(d.year, d.month, d.day)

        if coltype == TypeCodes.IP:
            off = self._offset
            self._offset += 16
            return ipaddress.ip_address(self._buf()[off : off + 16])

        if coltype == TypeCodes.IPV4:
            off = self._offset
            self._offset += 4
            return ipaddress.ip_address(self._buf()[off : off + 4])

        if coltype == TypeCodes.TIMESTAMP_NANOS:
            timestamp = self._get_long() / 1000000000.0
            return datetime.datetime.utcfromtimestamp(timestamp)

        if coltype == TypeCodes.TIME_NANOS:
            nanos = self._get_long()
            micros = int((nanos / 1000) % 1000000)
            float_seconds = nanos / 1000000000
            second = int(float_seconds % 60)
            minutes = float_seconds / 60
            minute = int(minutes % 60)
            hours = minutes / 60
            hour = int(hours % 24)

            return datetime.time(hour, minute, second, micros)

        if coltype == TypeCodes.TUPLE:
            return self._get_tuple()

        if coltype == TypeCodes.ST_LINESTRING:
            points = []
            num_elements = self._get_int()
            for i in range(num_elements):
                long = self._get_double()
                lat = self._get_double()
                points.append(_STPoint(long, lat))
            return _STLinestring(points)

        if coltype == TypeCodes.ST_POLYGON:
            exterior = []
            num_elements = self._get_int()
            for i in range(num_elements):
                long = self._get_double()
                lat = self._get_double()
                exterior.append(_STPoint(long, lat))
            holes = []
            num_rings = self._get_int()
            for i in range(num_rings):
                num_elements = self._get_int()
                ring = []
                for j in range(num_elements):
                    long = self._get_double()
                    lat = self._get_double()
                    ring.append(_STPoint(long, lat))
                holes.append(ring)
            return _STPolygon(exterior, holes)

        self.end_of_data = True
        raise Error(reason=f"Unknown column type {coltype}")

    def _get_byte(self) -> int:
        offset = self._offset
        self._offset += 1
        return self._buf()[offset]

    def _get_int(self) -> int:
        offset = self._offset
        self._offset += 4
        r = _unpack_int(self._buf(), offset)[0]
        assert isinstance(r, int)
        return r

    def _get_long(self) -> int:
        offset = self._offset
        self._offset += 8
        r = _unpack_long(self._buf(), offset)[0]
        assert isinstance(r, int)
        return r

    def _get_double(self) -> float:
        offset = self._offset
        self._offset += 8
        r = _unpack_double(self._buf(), offset)[0]
        assert isinstance(r, float)
        return r

    def _get_type(self, datalen: int, unpacker: Callable[[bytes, int], Tuple[_T, ...]]) -> _T:
        offset = self._offset
        self._offset += datalen
        return unpacker(self._buf(), offset)[0]

    def _get_array(self, level: int) -> List[object]:
        array: List[object] = []

        num_elements = self._get_int()

        all_null = self._get_byte()

        if all_null != 0:
            return []

        for _ in range(num_elements):
            if level > 0:
                array.append(self._get_array(level - 1))
            else:
                array.append(self._decode_entry())

        return array

    def _close_resultset(self) -> None:
        req = proto.Request()
        req.type = proto.Request.RequestType.Value("CLOSE_RESULT_SET")  # type: ignore # https://github.com/protocolbuffers/protobuf/issues/10240

        _send_msg(self.connection, req)

        rsp = _recv_msg(self.connection, proto.ConfirmationResponse())

        if rsp.type == proto.ConfirmationResponse.RESPONSE_WARN:
            warn(rsp.reason)
        elif not rsp.type == proto.ConfirmationResponse.RESPONSE_OK:
            raise _convert_exception(rsp)

    def _get_tuple(self) -> Tuple[object, ...]:
        num_elements = self._get_int()
        restuple: Tuple[object, ...] = ()
        for _ in range(num_elements):
            restuple += (self._decode_entry(),)
        return restuple


def connect(
    dsn: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    database: Optional[str] = None,
    tls: Optional[Union[int, str]] = None,
    force: Optional[bool] = None,
    handshake: Optional[Union[int, str]] = "gcm",
    configfile: Optional[str] = None,
) -> Connection:
    # pylint: disable=too-many-arguments
    """Create a new database connection.

    The connection parameters can be specified as part of the dsn,
    using keyword arguments or both.  If both are specified, the keyword
    parameter overrides the value in the dsn.

    The Ocient DSN is of the format:
    `ocient://user:password@[host][:port][/database][?param1=value1&...]`

    `user` and `password` must be supplied.  `host` defaults to localhost,
    port defaults to 4050, database defaults to `system` and `tls` defaults
    to `unverified`.

    Multiple hosts may be specified, separated by a comma, in which case the
    hosts will be tried in order  Thus an example DSN might be
    `ocient://someone:somepassword@host1,host2:4051/mydb`

    configfile specifies the name of a configuration file in INI format. See
    the Connection class for more detailed documentation.

    Currently supported parameters are:

    - tls: Which can have the values "off", "unverified", or "on" in the dsn,
         or Connection.TLS_NONE, Connection.TLS_UNVERIFIED, or
         Connection.TLS_ON as a keyword parameter.
    - handshake: "CBC", "GCM", or "SSO". "GCM" (Galois Counter Mode) should be used over "CBC" (Cipher Block Chaining) for password encryption. "SSO" for single sign on.
    - force: force the connection to remain on this host
    """
    if isinstance(handshake, str):
        if handshake.lower() == "gcm":
            handshake = Connection.HANDSHAKE_GCM
        elif handshake.lower() == "cbc":
            handshake = Connection.HANDSHAKE_CBC
        elif handshake.lower() == "sso":
            handshake = Connection.HANDSHAKE_SSO
        else:
            raise RuntimeError(f"Unknown Handshake method {handshake}")

    if isinstance(tls, str):
        if tls.lower() == "on":
            tls = Connection.TLS_ON
        elif tls.lower() == "unverified":
            tls = Connection.TLS_UNVERIFIED
        elif tls.lower() == "off":
            tls = Connection.TLS_NONE
        else:
            raise RuntimeError(f"Unknown TLS mode {tls}")

    params = {
        "user": user,
        "password": "*****",
        "host": host,
        "database": database,
        "tls": tls,
        "handshake": handshake,
    }

    logger.debug(f"Connect {params}")

    return Connection(dsn, user, password, host, database, tls, handshake, force, configfile)
