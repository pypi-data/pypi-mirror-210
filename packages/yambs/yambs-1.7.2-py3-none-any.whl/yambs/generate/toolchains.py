"""
A module for generating toolchain-related files.
"""

# third-party
from jinja2 import Environment

# internal
from yambs.environment import BuildEnvironment
from yambs.generate.common import render_template


def generate(jinja: Environment, env: BuildEnvironment) -> None:
    """Generate toolchain-related ninja files."""

    for name, data in env.config.data["toolchains"].items():
        toolchains_root = env.ninja_root.joinpath("toolchains", name)
        toolchains_root.mkdir(parents=True, exist_ok=True)

        render_template(
            jinja,
            toolchains_root,
            "toolchain.ninja",
            data,
        )
