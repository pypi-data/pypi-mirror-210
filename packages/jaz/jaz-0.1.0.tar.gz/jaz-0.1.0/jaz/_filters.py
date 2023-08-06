from __future__ import annotations

import os
import shlex
import subprocess
from typing import Any
from typing import Callable

import typer


try:
    from ansible.plugins.test.core import TestModule
    from ansible.plugins.filter.core import FilterModule

    _ANSIBLE_IS_AVAILABLE = True
except ImportError:
    _ANSIBLE_IS_AVAILABLE = False


def filter_env(value: str, default: str = "") -> str:
    return os.environ.get(value, default)


def run(
    cmd: str,
    check: bool = True,
    shell: bool = False,
    timeout: float = 2,
) -> subprocess.CompletedProcess[str]:
    args: str | list[str]
    if shell:
        args = cmd
    else:
        args = shlex.split(cmd)
    try:
        result = subprocess.run(
            args=args,
            check=False,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"Command '{cmd}' timed out after waiting for {timeout} seconds")
        raise typer.Exit(code=1)
    if check and result.returncode:
        errno = result.returncode
        error = result.stderr.strip()
        print(f"Command '{cmd}' returned non-zero: {errno}\n{error}")
        raise typer.Exit(code=1)
    return result


def filter_shell(
    cmd: str,
    strip: bool = True,
    check: bool = True,
    timeout: float = 2,
) -> str:
    result = run(cmd, check=check, timeout=timeout, shell=False)
    output = result.stdout
    if strip:
        output = output.strip()
    return output


FILTERS: dict[str, Callable[[Any], Any]] = {
    "env": filter_env,
    "shell": filter_shell,
}


if _ANSIBLE_IS_AVAILABLE:
    FILTERS.update(FilterModule().filters())
    FILTERS.update(TestModule().tests())
