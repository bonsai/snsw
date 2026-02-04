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


@app.command(help="Split WAV into chunks optimized for XTTS (target 8-11s).")
def split_xtts(
    input_wav: Path = typer.Argument(..., exists=True, help="Input wav file"),
    out_dir: Path = typer.Option(Path("data/clips_xtts"), help="Output directory"),
    min_s: float = typer.Option(6.0, help="Minimum duration to keep (s)"),
    max_s: float = typer.Option(11.0, help="Target maximum duration (s)"),
    silence_thresh_dbfs: int = typer.Option(-40, help="Silence threshold in dBFS"),
) -> None:
    """
    Split audio into chunks suitable for XTTS fine-tuning (around 10s).
    Uses a recursive strategy to break down long segments.
    """
    _require_ffmpeg()
    _require_ffmpeg()
    
    # Constants for XTTS splitting logic
    MIN_SILENCE_MS_THRESHOLD = 200
    SILENCE_REDUCTION_FACTOR = 0.7
    INITIAL_SILENCE_MS = 1000
    MIN_CLIP_SKIP_THRESHOLD_S = 2.0
    try:
        from pydub import AudioSegment  # type: ignore
        from pydub.silence import split_on_silence  # type: ignore
    except Exception as e:
        raise MissingDependencyError("pydub がインストールされていません") from e

    ensure_dir(out_dir)
    audio = AudioSegment.from_wav(input_wav)
    console.print(f"[bold]Splitting for XTTS[/bold] {input_wav} (target {min_s}-{max_s}s)")

    def recursive_split(chunk: AudioSegment, min_silence_ms: int) -> list[AudioSegment]:
        if len(chunk) <= max_s * 1000:
            return [chunk]
        
        # If min_silence_ms is too small, we might be cutting words. Stop recursing.
        if min_silence_ms < 200:
            # Fallback: simple slice (not ideal but better than crash)
            # Or return as is and let the filter handle it?
            # Let's just slice it fixed width as last resort
            return [chunk[i:i + int(max_s * 1000)] for i in range(0, len(chunk), int(max_s * 1000))]

        sub_chunks = split_on_silence(
            chunk,
            min_silence_len=min_silence_ms,
            silence_thresh=silence_thresh_dbfs,
            keep_silence=True, # Keep all silence to preserve "ma"
        )
        
        if not sub_chunks or (len(sub_chunks) == 1 and len(sub_chunks[0]) == len(chunk)):
            # Failed to split, try with smaller silence
            return recursive_split(chunk, int(min_silence_ms * SILENCE_REDUCTION_FACTOR))
            
        final_chunks = []
        for sub in sub_chunks:
            final_chunks.extend(recursive_split(sub, min_silence_ms))
            
        return final_chunks

    # Start with a generous silence length
    initial_chunks = recursive_split(audio, 1000)
    
    # Filter and export
    stem = input_wav.stem
    idx = 0
    skipped = 0
    
    for chunk in initial_chunks:
        duration_s = len(chunk) / 1000.0
        if duration_s < min_s:
            # Too short, maybe we can merge?
            # For now, just skip extremely short ones (< 2s) to avoid garbage
            if duration_s < 2.0:
                skipped += 1
                continue
            # Keep 2s-6s chunks, they might be useful
        
        out_path = out_dir / f"{stem}_{idx:05}.wav"
        chunk.export(out_path, format="wav")
        idx += 1

    console.print(f"[green]Done[/green] Created {idx} clips in {out_dir} (skipped {skipped} short clips)")

