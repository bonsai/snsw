from __future__ import annotations

import json
from pathlib import Path

import typer

from snsw.console import console
from snsw.errors import MissingDependencyError
from snsw.util import ensure_dir

app = typer.Typer(no_args_is_help=True)


def _load_model(model_size: str, device: str, compute_type: str):
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as e:  # pragma: no cover
        raise MissingDependencyError(
            "faster-whisper が必要です: pip install -e '.[whisper]'"
        ) from e

    return WhisperModel(model_size, device=device, compute_type=compute_type)


@app.command(help="Transcribe *.wav clips in a directory and write <clip>.txt sidecars.")
def clips(
    clips_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    language: str = typer.Option("ja", help="Language code (e.g. ja)"),
    model_size: str = typer.Option("large-v3", help="Whisper model size"),
    device: str = typer.Option("auto", help="auto|cpu|cuda"),
    compute_type: str = typer.Option("auto", help="auto|int8|float16|float32"),
    out_manifest: Path = typer.Option(
        Path("data/transcripts.jsonl"), help="Write JSONL manifest here"
    ),
) -> None:
    wavs = sorted(clips_dir.glob("*.wav"))
    if not wavs:
        console.print(f"[yellow]No wav files in[/yellow] {clips_dir}")
        raise typer.Exit(code=1)

    model = _load_model(model_size=model_size, device=device, compute_type=compute_type)
    ensure_dir(out_manifest.parent)

    console.print(f"[bold]Transcribing[/bold] {len(wavs)} clips (lang={language}, model={model_size})")

    with out_manifest.open("w", encoding="utf-8") as mf:
        for wav in wavs:
            segments, info = model.transcribe(
                str(wav),
                language=language,
                vad_filter=True,
            )
            text = "".join(seg.text for seg in segments).strip()
            sidecar = wav.with_suffix(".txt")
            sidecar.write_text(text + "\n", encoding="utf-8")

            mf.write(
                json.dumps(
                    {
                        "wav": str(wav),
                        "text": text,
                        "language": language,
                        "duration": getattr(info, "duration", None),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    console.print(f"[green]Done[/green] sidecars + {out_manifest}")
