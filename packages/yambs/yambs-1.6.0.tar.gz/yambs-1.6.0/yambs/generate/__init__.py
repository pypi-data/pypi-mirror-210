"""
A module for generating templated outputs.
"""

# built-in
from typing import Any, Dict

# third-party
from datazen.templates import environment
from jinja2 import FileSystemLoader
from vcorelib.io import ARBITER
from vcorelib.paths import resource

# internal
from yambs import PKG_NAME
from yambs.environment import BuildEnvironment
from yambs.generate.architectures import generate as generate_architectures
from yambs.generate.boards import generate as generate_boards
from yambs.generate.chips import generate as generate_chips
from yambs.generate.common import render_template
from yambs.generate.toolchains import generate as generate_toolchains


def generate(env: BuildEnvironment) -> None:
    """Generate ninja files."""

    templates_dir = resource("templates", package=PKG_NAME)
    assert templates_dir is not None

    jinja = environment(
        loader=FileSystemLoader([templates_dir], followlinks=True)
    )

    # Render the top-level configuration. This is the only file that's
    # generated into the root directory.
    render_template(jinja, env.config.root, "build.ninja", env.config.data)

    # Generate all other files.
    for gen in [
        generate_chips,
        generate_toolchains,
        generate_architectures,
        generate_boards,
    ]:
        gen(jinja, env)

    board_apps: Dict[str, Any] = {}

    # Ensure that the build root directory is present in the full output paths
    # for built applications.
    for board in env.config.board_data:
        board_apps[board.name] = {
            short: str(env.config.build_root.joinpath(path))
            for short, path in board.apps.items()
        }

    ARBITER.encode(
        env.ninja_root.joinpath("board_apps.json"),
        board_apps,
    )
