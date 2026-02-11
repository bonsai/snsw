from __future__ import annotations

from pathlib import Path

import typer

from snsw.console import console
from snsw.dataset import build_ljspeech_dataset

app = typer.Typer(no_args_is_help=True)


@app.command(help="Build LJSpeech-like dataset from clips (*.wav + *.txt sidecars).")
def build(
    clips_dir: Path = typer.Argument(..., exists=True, file_okay=False, help="Directory with clips"),
    out_dir: Path = typer.Option(Path("datasets/ljspeech"), help="Output dataset directory"),
    hardlink: bool = typer.Option(
        False,
        help="Use hardlinks instead of copying wavs (falls back to copy if unsupported)",
    ),
) -> None:
    wavs_dir, metadata = build_ljspeech_dataset(clips_dir=clips_dir, out_dir=out_dir, hardlink=hardlink)
    console.print(f"[green]Done[/green] wavs={wavs_dir} metadata={metadata}")
