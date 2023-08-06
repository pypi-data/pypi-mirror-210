"""
A module implementing a build environment state manager.
"""

# built-in
from pathlib import Path
from typing import Dict, Iterator, NamedTuple, Set, Tuple

# third-party
from vcorelib.logging import LoggerMixin

# internal
from yambs.config import Config
from yambs.config.board import Board
from yambs.translation import SourceTranslator, get_translator

SourceAndTranslator = Tuple[Path, SourceTranslator]


class SourceSets(NamedTuple):
    """A structure for managing different kinds of source paths."""

    regular: Set[Path]
    apps: Set[Path]

    def sources(self) -> Iterator[SourceAndTranslator]:
        """Iterate over sources and their source translator."""
        for source in self.regular:
            yield source, get_translator(source)

    def link_sources(self) -> Iterator[SourceAndTranslator]:
        """Get all sources that are directly provided to the linker."""

        for source, trans in self.sources():
            if trans.gets_linked:
                yield source, trans

    def implicit_sources(self) -> Iterator[SourceAndTranslator]:
        """Iterate over generated sources."""

        for source, trans in self.sources():
            if trans.generated_header:
                yield source, trans


class BuildEnvironment(LoggerMixin):
    """A class implementing a simple build environment."""

    def __init__(self, config: Config) -> None:
        """Initialize this instance."""

        super().__init__()

        self.config = config

        self.ninja_root = self.config.directory("ninja_out")

        # Keep track of all overall sources, so that no duplicate rules are
        # generated.
        self.global_sources: Set[Path] = set()

        # Keep track of sources by board.
        self.by_board: Dict[Board, SourceSets] = {}

    def set_board_sources(
        self, board: Board, regular: Set[Path], apps: Set[Path]
    ) -> SourceSets:
        """Finalize source sets for a given board."""

        assert board not in self.by_board, board
        sources = SourceSets(regular, apps)
        self.by_board[board] = sources

        self.logger.info(
            "(%s) Found %d sources and %d applications.",
            board.name,
            len(sources.regular),
            len(sources.apps),
        )

        return sources
