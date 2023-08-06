from __future__ import annotations

import enum
import os
import pathlib
import sys

import jinja2

from ._filters import FILTERS
from ._globals import GLOBALS


class UNDEFINED(str, enum.Enum):
    DEFAULT = "default"
    DEBUG = "debug"
    STRICT = "strict"

    def __str__(self) -> str:
        return self.value


UNDEFINED_MAPPING = {
    UNDEFINED.DEFAULT: jinja2.Undefined,
    UNDEFINED.DEBUG: jinja2.DebugUndefined,
    UNDEFINED.STRICT: jinja2.StrictUndefined,
}


def render(
    *,
    path: pathlib.Path,
    no_env: bool,
    output: pathlib.Path | None,
    undefined: UNDEFINED,
) -> None:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path),
        undefined=UNDEFINED_MAPPING[undefined],
    )
    env.filters.update(FILTERS)
    env.globals.update(GLOBALS)
    if not no_env:
        env.globals.update(os.environ)

    contents = sys.stdin.read() if str(path) == "-" else path.read_text()
    template = env.from_string(contents)
    rendered = template.render()
    if output:
        output.write_text(rendered)
    else:
        sys.stdout.write(rendered)
