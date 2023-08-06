"""
A module with interfaces for describing how sources are translated into
outputs.
"""

# built-in
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple, Optional


class SourceTranslator(NamedTuple):
    """
    A structure for keeping track of how source files become different types
    of output files.
    """

    rule: str = "cc"
    output_extension: str = ".o"
    dest: Path = Path("$build_dir")

    def output(self, path: Path) -> Path:
        """Get the output file from a given path."""
        return self.dest.joinpath(path.with_suffix(self.output_extension))

    @property
    def gets_linked(self) -> bool:
        """
        Determine if this source's output gets linked into a final image or
        executable.
        """
        return self.output_extension == ".o"

    @property
    def generated_header(self) -> bool:
        """Determine if this translation produces a header file."""
        return self.output_extension == ".h"


DEFAULT = SourceTranslator()


SOURCES = {
    ".c": DEFAULT,
    ".S": DEFAULT,
    ".cc": DEFAULT,
    ".pio": SourceTranslator("pio", ".h", Path("$generated_dir")),
}


@lru_cache(maxsize=None)
def is_source(path: Path) -> Optional[SourceTranslator]:
    """Determine if a file is a source file."""
    return SOURCES.get(path.suffix)


def get_translator(path: Path) -> SourceTranslator:
    """Get the source translator for a given source."""

    result = is_source(path)
    assert result is not None
    return result
