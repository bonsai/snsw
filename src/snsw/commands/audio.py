from __future__ import annotations

from pathlib import Path

import typer

from snsw.console import console
from snsw.errors import MissingDependencyError
from snsw.util import ensure_dir, which

app = typer.Typer(no_args_is_help=True)


def _require_ffmpeg() -> None:
    if which("ffmpeg") is None:
        raise MissingDependencyError(
            "ffmpeg が見つかりません。ffmpeg をインストールして PATH に追加してください。"
        )


@app.command(help="Convert an audio file to WAV (mono / 16-bit / sample-rate).")
def to_wav(
    input_path: Path = typer.Argument(..., exists=True, help="Input audio/video file"),
    output_path: Path = typer.Option(
        None,  # type: ignore[assignment]
        "--out",
        help="Output wav path (default: <input>.wav next to input)",
    ),
    sample_rate: int = typer.Option(22050, help="Target sample rate"),
    channels: int = typer.Option(1, help="Target channels (1=mono)"),
) -> None:
    _require_ffmpeg()

    try:
        from pydub import AudioSegment  # type: ignore
    except Exception as e:  # pragma: no cover
        raise MissingDependencyError("pydub がインストールされていません") from e

    if output_path is None:
        output_path = input_path.with_suffix(".wav")

    console.print(f"[bold]Converting[/bold] {input_path} -> {output_path}")

    audio = AudioSegment.from_file(input_path)
    audio = (
        audio.set_frame_rate(sample_rate)
        .set_channels(channels)
        .set_sample_width(2)  # 16-bit
    )

    ensure_dir(output_path.parent)
    audio.export(output_path, format="wav")

    console.print("[green]Done[/green]")


@app.command(help="Split WAV into chunks using silence detection.")
def split_silence(
    input_wav: Path = typer.Argument(..., exists=True, help="Input wav file"),
    out_dir: Path = typer.Option(Path("data/clips"), help="Output directory"),
    min_silence_len_ms: int = typer.Option(700, help="Min silence length (ms)"),
    silence_thresh_dbfs: int = typer.Option(
        -40, help="Silence threshold in dBFS (e.g. -40)"
    ),
    keep_silence_ms: int = typer.Option(200, help="Keep some silence around chunks (ms)"),
    max_chunk_s: float = typer.Option(
        20.0, help="If a chunk is longer than this, split it into fixed-size pieces"
    ),
) -> None:
    _require_ffmpeg()

    try:
        from pydub import AudioSegment  # type: ignore
        from pydub.silence import split_on_silence  # type: ignore
    except Exception as e:  # pragma: no cover
        raise MissingDependencyError("pydub がインストールされていません") from e

    ensure_dir(out_dir)
    audio = AudioSegment.from_wav(input_wav)

    console.print(f"[bold]Splitting[/bold] {input_wav}")

    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len_ms,
        silence_thresh=silence_thresh_dbfs,
        keep_silence=keep_silence_ms,
    )

    if not chunks:
        console.print("[yellow]No chunks produced[/yellow]")
        raise typer.Exit(code=1)

    max_ms = int(max_chunk_s * 1000)
    stem = input_wav.stem

    idx = 0
    for chunk in chunks:
        if len(chunk) <= 0:
            continue

        if len(chunk) <= max_ms:
            out_path = out_dir / f"{stem}_{idx:05}.wav"
            chunk.export(out_path, format="wav")
            idx += 1
            continue

        # Split too-long chunk into fixed-size pieces.
        for start_ms in range(0, len(chunk), max_ms):
            piece = chunk[start_ms : start_ms + max_ms]
            out_path = out_dir / f"{stem}_{idx:05}.wav"
            piece.export(out_path, format="wav")
            idx += 1

    console.print(f"[green]Done[/green] - {idx} clips -> {out_dir}")
