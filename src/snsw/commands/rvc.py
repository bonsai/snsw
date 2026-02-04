from __future__ import annotations

import shlex
from pathlib import Path

import typer

from snsw.console import console
from snsw.util import ensure_dir, run

app = typer.Typer(no_args_is_help=True)


@app.command(
    help="Run an external RVC conversion command.",
)
def convert(
    input_wav: Path = typer.Argument(..., exists=True, help="Input wav"),
    out_wav: Path = typer.Option(Path("outputs/rvc.wav"), help="Output wav"),
    template: str = typer.Option(
        ...,  # required
        help=(
            "Command template. Use {in} and {out} placeholders. Example: "
            "python path/to/infer_cli.py --model models/shinsho.pth --input {in} --output {out}"
        ),
    ),
) -> None:
    ensure_dir(out_wav.parent)

    cmd_str = template.format(in=str(input_wav), out=str(out_wav))
    cmd = shlex.split(cmd_str, posix=False)

    console.print("[bold]Running[/bold] " + cmd_str)
    run(cmd)
    console.print(f"[green]Done[/green] {out_wav}")
