from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from snsw.errors import ExternalToolError


def which(tool: str) -> str | None:
    return shutil.which(tool)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise ExternalToolError(
            f"Command failed (exit {proc.returncode}): {' '.join(cmd)}\n{proc.stderr.strip()}"
        )
