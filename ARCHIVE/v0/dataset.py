from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from snsw.util import ensure_dir


@dataclass(frozen=True)
class Clip:
    wav_path: Path
    text: str


def sanitize_text(text: str) -> str:
    # Keep it simple and training-friendly: collapse whitespace and strip.
    return " ".join(text.replace("\u3000", " ").split()).strip()


def load_clips_from_sidecars(clips_dir: Path) -> list[Clip]:
    clips: list[Clip] = []
    for wav in sorted(clips_dir.glob("*.wav")):
        sidecar = wav.with_suffix(".txt")
        if not sidecar.exists():
            continue
        text = sanitize_text(sidecar.read_text(encoding="utf-8"))
        if not text:
            continue
        clips.append(Clip(wav_path=wav, text=text))
    return clips


def _copy_or_link(src: Path, dst: Path, *, hardlink: bool) -> None:
    ensure_dir(dst.parent)
    if hardlink:
        try:
            if dst.exists():
                dst.unlink()
            os.link(src, dst)
            return
        except OSError:
            # Fall back to copy.
            pass
    shutil.copy2(src, dst)


def build_ljspeech_dataset(
    *,
    clips_dir: Path,
    out_dir: Path,
    hardlink: bool = False,
) -> tuple[Path, Path]:
    """Build a simple dataset: <out_dir>/wavs/*.wav + metadata.csv

    Returns:
      (wavs_dir, metadata_csv_path)
    """
    clips = load_clips_from_sidecars(clips_dir)
    if not clips:
        raise ValueError(f"No clips found in {clips_dir} (expected *.wav + *.txt sidecars)")

    wavs_dir = ensure_dir(out_dir / "wavs")
    metadata_path = out_dir / "metadata.csv"

    lines: list[str] = []
    for clip in clips:
        rel_wav = f"wavs/{clip.wav_path.name}"
        dst_wav = wavs_dir / clip.wav_path.name
        _copy_or_link(clip.wav_path, dst_wav, hardlink=hardlink)
        # LJSpeech format: wav_path|transcript|normalized (we keep normalized same)
        lines.append(f"{rel_wav}|{clip.text}|{clip.text}")

    ensure_dir(out_dir)
    metadata_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return wavs_dir, metadata_path
