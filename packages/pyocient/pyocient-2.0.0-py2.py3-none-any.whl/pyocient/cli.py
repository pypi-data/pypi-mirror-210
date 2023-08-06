import datetime
import decimal
import ipaddress
import logging
import os
import pathlib
import sys
import uuid
import warnings
from time import time_ns
from typing import TYPE_CHECKING, Callable, List, NamedTuple, Optional, Tuple, Union

from prompt_toolkit.history import FileHistory

from pyocient.api import Connection, SQLException, TypeCodes, _STLinestring, _STPoint, _STPolygon, connect
from pyocient.pkg_version import __version__ as version


def _custom_type_to_json(obj: object) -> Union[str, List[int]]:
    """Helper function to convert types returned from queries to
    JSON values.  Typically invoked passed as the `default` parameter
    to json.dumps as in:

    `json.dumps(some_rows, default=_custom_type_to_json)`
    """
    if isinstance(obj, decimal.Decimal):
        return str(obj)

    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()

    if isinstance(obj, bytes):
        return list(obj)

    if isinstance(obj, (uuid.UUID, ipaddress.IPv4Address, ipaddress.IPv6Address)):
        return str(obj)

    if isinstance(obj, (_STPoint, _STLinestring, _STPolygon)):
        # TODO GeoJSON??
        return str(obj)

    print(f"type_to_string got called for type {type(obj)}", file=sys.stderr)
    return f"placeholder for {type(obj)}"


class IgnoreSpaceFileHistory(FileHistory):
    def __init__(self, filename: str):
        super().__init__(filename=filename)

    def _is_sensitive_cmd(self, string: str) -> bool:
        return string[:1].isspace()

    def append_string(self, string: str) -> None:
        # Like the UNIX ignorespace option, causes lines which begin with a
        # white space character to be omitted from the history file.
        if not string[:1].isspace():
            super().append_string(string)


class ReadOnlyFileHistory(IgnoreSpaceFileHistory):
    def __init__(self, filename: str):
        super().__init__(filename=filename)

    def store_string(self, string: str) -> None:
        pass


if TYPE_CHECKING:
    from argparse import ArgumentParser


def argparser() -> "ArgumentParser":
    from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter

    configfile = pathlib.Path.home() / ".pyocient"

    parser = ArgumentParser(
        description=f"""Ocient Python client {version}.
In the simplest case, run with a Data Source Name (dsn) and a
query.  For example:
  pyocient ocient://user:password@myhost:4050/mydb "select * from mytable"

Multiple query strings may be provided

DSN's are of the form:
  ocient://user:password@[host][:port][/database][?param1=value1&...]

Supported parameter are:

- tls: Which can have the values "off", "unverified", or "on"

- force: true or false to force the connection to stay on this server

- handshake: Which can have the value "cbc"

Multiple hosts may be specified, separated by a comma, in which case the
hosts will be tried in order  Thus an example DSN might be
`ocient://someone:somepassword@host1,host2:4051/mydb`

When running in the command line interface, the following extra commands
are supported:

- connect to 'ocient://....' user someuser using somepassword;

    when the DSN follows the normal pyocient DSN format, but the userid and password may be passed
    using the USER and USING keywords (similar to the Ocient JDBC driver).  The DSN must be quoted.

- source 'file';

    Execute the statements from the specified file.  The file name must be quoted.

- set format table;

    Set the output format 

- quit;

""",
        formatter_class=RawDescriptionHelpFormatter,
    )

    # Flags that apply to both execution modes
    outgroup = parser.add_mutually_exclusive_group()
    outgroup.add_argument("-o", "--outfile", type=FileType("w"), default="-", help="Output file")
    outgroup.add_argument(
        "-n",
        "--noout",
        action="store_const",
        const=None,
        dest="outfile",
        help="Do not output results",
    )
    configgroup = parser.add_mutually_exclusive_group()
    configgroup.add_argument(
        "-c",
        "--configfile",
        type=str,
        default=str(configfile),
        help="Configuration file",
    )
    configgroup.add_argument(
        "--noconfig",
        action="store_const",
        const=None,
        dest="configfile",
        help="No configuration file",
    )
    parser.add_argument(
        "-i",
        "--infile",
        type=FileType("r"),
        default=None,
        help="Input file containing SQL statements",
    )
    parser.add_argument(
        "-e",
        "--echo",
        action="store_true",
        help="Echo statements in output",
    )
    parser.add_argument(
        "-l",
        "--loglevel",
        type=str,
        default="critical",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Logging level, defaults to critical",
    )
    parser.add_argument("--logfile", type=FileType("a"), default=sys.stdout, help="Log file")
    parser.add_argument("-t", "--time", action="store_true", help="Output query time")
    parser.add_argument(
        "dsn",
        nargs="?",
        help="DSN of the form ocient://user:password@[host][:port][/database][?param1=value1&...]",
    )
    parser.add_argument("sql", nargs="?", help="SQL statement")
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        choices=["json", "table", "csv"],
        default="json",
        help="Output format, defaults to json",
    )
    parser.add_argument(
        "--nocolor",
        action="store_true",
        help="When using pyocient interactively, do not color",
    )
    parser.add_argument(
        "--nohistory",
        action="store_true",
        help="When using pyocient interactively, do not store command history",
    )

    return parser


def main() -> int:
    import csv
    import json
    from argparse import Namespace

    from pygments.lexers.sql import SqlLexer  # type: ignore
    from pygments.token import Token  # type: ignore
    from tabulate import tabulate

    args = argparser().parse_args(sys.argv[1:])

    log_level = getattr(logging, args.loglevel.upper(), None)

    # Ensure that warnings are always displayed
    warnings.simplefilter("always", UserWarning)

    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log level: {args.loglevel}")

    logging.basicConfig(
        level=log_level,
        stream=args.logfile,
        format="[%(asctime)s][%(levelname)s] %(message)s",
    )

    sql_stmt = ""
    lexer = SqlLexer()

    def _unquote(input: str) -> str:
        """
        Unquote a string, with either single or double quotes
        """
        if input[0] == '"' and input[-1] == '"':
            return input[1:-1]
        if input[0] == "'" and input[-1] == "'":
            return input[1:-1]
        return input

    def _do_line(
        args: Namespace,
        connection: Optional[Connection],
        text: str,
        sql_stmt: str,
        query_fn: Callable[[Namespace, Optional[Connection], str], Tuple[Optional[Connection], int]],
    ) -> Tuple[str, Optional[Connection], int]:
        new_connection = connection
        for token_type, token_val in lexer.get_tokens(text):
            if token_type == Token.Punctuation and token_val == ";":
                (new_connection, return_code) = query_fn(args, new_connection, sql_stmt)
                sql_stmt = ""
            else:
                sql_stmt += token_val

        return (sql_stmt, new_connection, return_code)

    def _do_query(args: Namespace, connection: Optional[Connection], query: str) -> Tuple[Optional[Connection], int]:

        if args.echo:
            print(query, file=args.outfile)

        # First, see if this is something we should handle here in the CLI
        tokens = [
            token
            for (token_type, token) in lexer.get_tokens(query)
            if token_type
            in (
                Token.Keyword,
                Token.Name,
                Token.Literal.String.Symbol,
                Token.Literal.String.Single,
            )
        ]

        # connect to statement
        if len(tokens) > 1 and tokens[0].lower() == "connect" and tokens[1].lower() == "to":
            try:
                if len(tokens) == 7:
                    if tokens[3].lower() != "user" or tokens[5].lower() != "using":
                        print(f"Invalid USER or USING keywords on CONNECT TO", file=sys.stderr)
                        return (connection, os.EX_DATAERR)
                    dsn = _unquote(tokens[2])
                    user = _unquote(tokens[4])
                    password = _unquote(tokens[6])
                    return (connect(dsn, user=user, password=password, configfile=args.configfile), os.EX_OK)
                elif len(tokens) == 3:
                    dsn = _unquote(tokens[2])
                    return (connect(dsn, configfile=args.configfile), os.EX_OK)
                print(f"Invalid CONNECT TO statement {len(tokens)} {tokens}", file=sys.stderr)
                return (connection, os.EX_USAGE)
            except SQLException as e:
                print(e, file=sys.stderr)
                return (connection, os.EX_OSERR)

        # set format
        if len(tokens) > 2 and tokens[0].lower() == "set" and tokens[1].lower() == "format":
            new_format = tokens[2].lower()
            if new_format in ["json", "table", "csv"]:
                args.format = new_format
                print("OK", file=args.outfile)
                return (connection, os.EX_OK)
            else:
                print(f"Invalid output format {new_format}", file=sys.stderr)
                return (connection, os.EX_DATAERR)

        if (len(tokens) > 2) and tokens[0].lower() == "set" and tokens[1].lower() == "echo":
            echo_val = tokens[2].lower()
            if echo_val in ["on", "true", "1"]:
                args.echo = True
                return (connection, os.EX_OK)
            elif echo_val in ["off", "false", 0]:
                args.echo = False
                return (connection, os.EX_OK)
            else:
                print("Invalid echo statement", file=sys.stderr)
                return (connection, os.EX_DATAERR)

        # source
        if len(tokens) > 0 and tokens[0].lower() == "source":
            if len(tokens) != 2:
                print("Invalid SOURCE statement", file=sys.stderr)
                return (connection, os.EX_DATAERR)

            try:
                with open(_unquote(tokens[1]), mode="r") as f:
                    (sql_stmt, connection, return_code) = _do_line(args, connection, f.read(), "", _do_query)
                if len(sql_stmt.strip()):
                    connection, return_code = _do_query(args, connection, sql_stmt)
                return (connection, return_code)
            except Exception as e:
                print(e, file=sys.stderr)
                return (connection, os.EX_OSERR)

        # quit
        if len(tokens) > 0 and tokens[0].lower() == "quit":
            sys.exit(os.EX_OK)

        if connection is None:
            print(f"No active connection", file=sys.stderr)
            return (connection, os.EX_UNAVAILABLE)

        # OK, if we fall through to here, have the normal library handle it
        if args.time:
            starttime = time_ns()

        cursor = connection.cursor()

        result: Optional[List[NamedTuple]]
        try:
            cursor.execute(query)

            if cursor.description:
                result = cursor.fetchall()
            else:
                result = None
        except SQLException as e:
            print(e, file=sys.stderr)
            return (cursor.connection, os.EX_DATAERR)
        except KeyboardInterrupt:
            print("Operation interrupted.", file=sys.stderr)
            cur_conn = cursor.connection
            cur_conn.close()
            return (
                Connection(
                    user=cur_conn.user,
                    password=cur_conn.password,
                    host=",".join(cur_conn.hosts),
                    database=cur_conn.database,
                    tls=cur_conn.tls,
                    handshake=cur_conn.handshake,
                    force=cur_conn.force,
                    session=cur_conn.session,
                ),
                os.EX_IOERR,
            )

        if args.time:
            endtime = time_ns()

        if cursor.description is None:
            print("OK", file=args.outfile)

        elif args.outfile is not None:
            if cursor.generated_result and cursor.description[0][0] == "explain":
                to_dump = [{"explain": json.loads(cursor.generated_result)}]

                print(
                    json.dumps(to_dump, indent=4, default=_custom_type_to_json),
                    file=args.outfile,
                )
                result = None

            if result:
                # Preprocess bytes objects into desired str output, default to hex
                binary_column_idxs = [i for i, col in enumerate(cursor.description) if col[1] == TypeCodes.BINARY]
                if binary_column_idxs:
                    for i, row in enumerate(result):
                        for col_idx in binary_column_idxs:
                            col = row[col_idx]
                            if col is not None:
                                assert isinstance(col, bytes)
                                # N.B. this line relies on the assumption (true today) that
                                #      the NamedTuple `_fields` are in the same order as the
                                #      `cursor.description` tuples. This assumption allows
                                #      this line to look up the NamedTuple field name, which
                                #      importantly may differ from the column name due to
                                #      `rename=True` in the NamedTuple constructor, by its
                                #      column index.
                                result[i] = row._replace(**{row._fields[col_idx]: col.hex()})

                colnames = [c[0] for c in cursor.description]

                if args.format == "json":
                    dict_result = [row._asdict() for row in result]

                    print(
                        json.dumps(dict_result, indent=4, default=_custom_type_to_json),
                        file=args.outfile,
                    )
                elif args.format == "table":
                    print(
                        tabulate(
                            result,
                            headers=colnames,
                            tablefmt="psql",
                        ),
                        file=args.outfile,
                    )
                elif args.format == "csv":
                    csv.writer(args.outfile, quoting=csv.QUOTE_ALL).writerow(colnames)
                    writer = csv.writer(args.outfile)
                    for row in result:
                        writer.writerow(row)

        if args.time:
            endtime = time_ns()
            print(f"Execution time: {(endtime - starttime)/1000000000:.3f} seconds", file=args.outfile)

        if cursor.description and args.outfile.isatty():
            print(f"Fetched {cursor.rowcount} rows")
        # If we don't return this connection, then we end up using the old connection which we could have been redirected
        return (cursor.connection, os.EX_OK)

    def _do_repl(args: Namespace, connection: Optional[Connection]) -> None:
        from pathlib import Path

        from prompt_toolkit import PromptSession
        from prompt_toolkit.lexers import PygmentsLexer

        sql_stmt = ""

        history: Union[ReadOnlyFileHistory, IgnoreSpaceFileHistory]
        if args.nohistory:
            history = ReadOnlyFileHistory(str(Path.home() / ".pyocient_history"))
        else:
            history = IgnoreSpaceFileHistory(str(Path.home() / ".pyocient_history"))

        session: PromptSession[str]
        if args.nocolor:
            session = PromptSession(history=history)
        else:
            session = PromptSession(
                lexer=PygmentsLexer(SqlLexer),
                history=history,
            )

        if connection:
            cursor = connection.cursor()
            print(f"Ocient Database™", file=args.outfile)
            print(f"System Version: {cursor.getSystemVersion()}, Client Version {version}", file=args.outfile)
        eof = False
        text = ""
        while not eof:
            try:
                text = session.prompt("> ")
            except KeyboardInterrupt:
                sql_stmt = ""
                continue
            except EOFError:
                break
            (sql_stmt, connection, return_code) = _do_line(args, connection, text, sql_stmt, _do_query)

        if len(sql_stmt.strip()):
            (connection, return_code) = _do_query(args, connection, sql_stmt)

        print("GoodBye!", file=args.outfile)

    return_code = os.EX_OK
    try:
        if args.dsn:
            connection = connect(args.dsn, configfile=args.configfile)
        else:
            connection = None

        if args.sql:
            (connection, return_code) = _do_query(args, connection, args.sql)
        elif args.infile:
            (sql_stmt, connection, return_code) = _do_line(args, connection, args.infile.read(), sql_stmt, _do_query)
            if len(sql_stmt.strip()):
                (connection, return_code) = _do_query(args, connection, sql_stmt)
        elif sys.stdin.isatty():
            _do_repl(args, connection)
        else:
            (sql_stmt, connection, return_code) = _do_line(args, connection, sys.stdin.read(), sql_stmt, _do_query)

    except SQLException as exc:
        print(f"Error: {exc.reason}", file=sys.stderr)
        return_code = os.EX_DATAERR

    return return_code


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)
