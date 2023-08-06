# from __future__ import annotations
import pathlib
from importlib.metadata import version
from typing import Annotated
from typing import Optional

import typer

from . import api

# import shlex
# import subprocess
# from typing import Literal

# def do_subprocess(
#     cmd: str,
#     stdout: Optional[int] = subprocess.PIPE,
#     stderr: Optional[int] = subprocess.PIPE,
#     check: bool = True,
#     timeout: float = 2,
#
# ) -> str:
#     shell=True
#     try:
#         result = subprocess.run(
#             args=shlex.split(cmd),
#             stdout=stdout,
#             stderr=stderr,
#             check=False,
#             shell=shell,
#             timeout=timeout,
#         )
#     except subprocess.TimeoutExpired:
#         print(f"Command '{cmd}' timed out after waiting for {timeout} seconds")
#         raise typer.Exit(code=1)
#     if check and result.returncode:
#         errno = result.returncode
#         error = result.stderr.decode().strip()
#         print(f"Command '{cmd}' returned non-zero: {errno}\n{error}")
#         raise typer.Exit(code=1)
#     return result
#
#
# def do_shell(
#     cmd: str,
#     strip: bool = True,
#     check: bool = True,
#     timeout: float = 2
# ) -> str:
#     result = do_subprocess(cmd, stderr=False, check=check, timeout=timeout)
#     if not strip:
#         return result.stdout.decode(encoding=ENCODING)
#     else:
#         return result.stdout.decode(encoding=ENCODING).strip()


def version_callback(value: bool) -> None:
    if value:
        print(f"jaz {version('jaz')}")
        raise typer.Exit()


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
)


@app.command(no_args_is_help=True, help="Render jinja templates from the Command Line.")
def main(
    # fmt: off
    # path: Annotated[pathlib.Path, typer.Argument(allow_dash=True)],
    path: Annotated[pathlib.Path, typer.Argument(help="The path to the template file. Use '-' for STDIN.")],
    output: Annotated[Optional[pathlib.Path], typer.Argument(help="The path to write the rendered output. If not provided the output will be written on STDOUT.")] = None,
    # output: Annotated(pathlib.Path, typer.Argument)
    undefined: Annotated[api.UNDEFINED, typer.Option(help="Defines how jinja should treat underfined variables.")] = api.UNDEFINED.STRICT,
    no_env: Annotated[bool, typer.Option("--no-env", help="Don't inject environmental variables into jinja's global dictionary.")] = False,
    version: Annotated[Optional[bool], typer.Option("--version", callback=version_callback, is_eager=True, help="Display the version of jaz.")] = None,
    # fmt: on
) -> int:
    api.render(
        path=path,
        no_env=no_env,
        output=output,
        undefined=undefined,
    )
    return 0


if __name__ == "__main__":
    typer.run(main)
