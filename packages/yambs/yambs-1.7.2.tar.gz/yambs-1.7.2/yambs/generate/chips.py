"""
A module for generating chip-related files.
"""

# third-party
from jinja2 import Environment

# internal
from yambs.environment import BuildEnvironment
from yambs.generate.common import render_template


def generate(jinja: Environment, env: BuildEnvironment) -> None:
    """Generate chip-related ninja files."""

    for name, data in env.config.data["chips"].items():
        chips_root = env.ninja_root.joinpath("chips", name)
        chips_root.mkdir(parents=True, exist_ok=True)

        # Render chip files and linker scripts.
        render_template(
            jinja,
            chips_root,
            "chip.ninja",
            data,
        )
        render_template(
            jinja,
            chips_root,
            "chip.ld",
            data["linker"],
        )
