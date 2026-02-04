from __future__ import annotations

from pathlib import Path

import typer

from snsw.console import console
from snsw.errors import MissingDependencyError
from snsw.util import ensure_dir

app = typer.Typer(no_args_is_help=True)


def _load_tts(model_name: str, gpu: bool):
    try:
        from TTS.api import TTS  # type: ignore
    except Exception as e:  # pragma: no cover
        raise MissingDependencyError("Coqui TTS が必要です: pip install -e '.[tts]'") from e

    return TTS(model_name=model_name, gpu=gpu)


@app.command(help="Generate speech with XTTS-v2 voice cloning (zero-shot).")
def clone(
    text: str = typer.Argument(..., help="Text to speak"),
    speaker_wav: Path = typer.Option(
        ..., exists=True, help="Reference speaker wav (a few seconds to a few minutes)"
    ),
    out_wav: Path = typer.Option(Path("outputs/out.wav"), help="Output wav"),
    language: str = typer.Option("ja", help="Language code"),
    model_name: str = typer.Option(
        "tts_models/multilingual/multi-dataset/xtts_v2", help="Coqui model name"
    ),
    gpu: bool = typer.Option(True, help="Use GPU if available"),
) -> None:
    ensure_dir(out_wav.parent)
    tts = _load_tts(model_name=model_name, gpu=gpu)

    console.print("[bold]Generating[/bold]")
    tts.tts_to_file(
        text=text,
        speaker_wav=str(speaker_wav),
        language=language,
        file_path=str(out_wav),
    )
    console.print(f"[green]Done[/green] {out_wav}")
