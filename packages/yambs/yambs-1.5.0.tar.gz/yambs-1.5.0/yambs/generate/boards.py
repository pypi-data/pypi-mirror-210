"""
A module for generating board-related files.
"""

# built-in
from logging import getLogger
from os import linesep
from pathlib import Path
from typing import Any, Dict, Set, TextIO, Tuple

# third-party
from jinja2 import Environment
from vcorelib.paths import rel

# internal
from yambs.config import Config
from yambs.config.board import Board
from yambs.generate.common import is_source, render_template
from yambs.generate.ninja import (
    write_link_line,
    write_phony,
    write_source_line,
)

LOG = getLogger(__name__)


def add_dir(
    stream: TextIO,
    paths: Set[Path],
    path: Path,
    comment: str,
    base: Path,
    current_sources: Set[Path],
    board: Board,
    board_specific: bool = False,
) -> None:
    """Add a directory to set of paths."""

    LOG.debug("%s: checking '%s' for sources.", comment, path)

    if path.is_dir():
        stream.write(linesep + f"# {comment}." + linesep)
        for item in path.iterdir():
            if is_source(item):
                paths.add(
                    write_source_line(
                        stream,
                        item,
                        base,
                        current_sources,
                        board,
                        board_specific=board_specific,
                    )
                )


def create_paths_dict(root: Path, board: Board) -> Dict[str, Any]:
    """Create paths based on common pathing conventions."""

    chip = board.chip

    return {
        "Common": root.joinpath("common"),
        "Chip": root.joinpath("chips", chip.name),
        "Architecture": root.joinpath(chip.architecture.name),
        "CPU": root.joinpath(chip.cpu),
        "Board": root.joinpath("boards", board.name),
    }


def write_sources(
    stream: TextIO,
    board: Board,
    src_root: Path,
    global_sources: Set[Path],
) -> Tuple[Set[Path], Set[Path]]:
    """Write the source-file manifest."""

    # Add regular sources.
    all_srcs: Set[Path] = set()

    for kind, path in create_paths_dict(src_root, board).items():
        add_dir(
            stream,
            all_srcs,
            path,
            f"{kind} sources",
            src_root,
            global_sources,
            board,
        )

    # Add any extra sources this board specified.
    for extra in board.extra_dirs:
        add_dir(
            stream,
            all_srcs,
            src_root.joinpath("third-party", extra),
            "extra sources",
            src_root,
            global_sources,
            board,
        )

    # Add application sources.
    app_srcs: Set[Path] = set()
    for kind, path in create_paths_dict(
        src_root.joinpath("apps"), board
    ).items():
        add_dir(
            stream,
            app_srcs,
            path,
            f"{kind} application sources",
            src_root,
            global_sources,
            board,
            # Avoid having a redundant directory in the path when the source
            # directory is already the board-specific one.
            board_specific="boards" not in str(path),
        )

    return all_srcs, app_srcs


def generate(
    jinja: Environment,
    ninja_root: Path,
    config: Config,
) -> None:
    """Generate board-related ninja files."""

    # Render the board manifest and rules file.
    for template in ["all.ninja", "rules.ninja"]:
        render_template(jinja, ninja_root, template, config.data)

    src_root = rel(config.src_root)

    # Keep track of all overall sources, so that no duplicate rules are
    # generated.
    global_sources: Set[Path] = set()

    for board, raw_data in config.boards():
        board_root = ninja_root.joinpath("boards", board.name)
        board_root.mkdir(parents=True, exist_ok=True)
        render_template(jinja, board_root, "board.ninja", raw_data)

        # Perform source-file discovery.
        with board_root.joinpath("sources.ninja").open("w") as path_fd:
            path_fd.write(f"src_dir = {config.data['src_root']}" + linesep)

            all_srcs, app_srcs = write_sources(
                path_fd, board, src_root, global_sources
            )

        LOG.info(
            "(%s) Found %d sources and %d applications.",
            board.name,
            len(all_srcs),
            len(app_srcs),
        )

        # Write the application manifest.
        with board_root.joinpath("apps.ninja").open("w") as path_fd:
            for app_src in app_srcs:
                write_link_line(path_fd, app_src, all_srcs, src_root, board)

            # Write the phony target.
            path_fd.write("# A target to build all applications." + linesep)
            write_phony(path_fd, app_srcs, src_root, board.name)
