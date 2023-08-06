"""
A module for writing formatting-related ninja build rules.
"""

# built-in
from os import linesep
from typing import TextIO

# internal
from yambs.environment import BuildEnvironment
from yambs.generate.ninja import write_continuation


def write_format_target(stream: TextIO, env: BuildEnvironment) -> None:
    """
    Write rules and targets for running clang-format on first-party sources
    and headers.
    """

    stream.write("rule clang-format" + linesep)
    stream.write("  command = clang-format -i $in" + linesep + linesep)

    to_format = list(env.first_party_sources_headers())
    if to_format:
        line = "build format: clang-format "
        offset = " " * len(line)

        stream.write(line)
        stream.write(str(to_format[0]))

        for source in to_format[1:]:
            write_continuation(stream, offset)
            stream.write(str(source))

        stream.write(linesep)
