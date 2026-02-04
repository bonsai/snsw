from __future__ import annotations

from pathlib import Path

import pytest

from snsw.dataset import build_ljspeech_dataset, sanitize_text


def test_sanitize_text_collapses_whitespace() -> None:
    assert sanitize_text("  a\n\tb  ") == "a b"
    assert sanitize_text("あ\u3000い") == "あ い"


def test_build_dataset_from_sidecars(tmp_path: Path) -> None:
    clips = tmp_path / "clips"
    clips.mkdir()

    wav1 = clips / "clip_00001.wav"
    txt1 = clips / "clip_00001.txt"
    wav1.write_bytes(b"RIFF....")
    txt1.write_text("  こんにちは\n", encoding="utf-8")

    out_dir = tmp_path / "dataset"
    wavs_dir, meta = build_ljspeech_dataset(clips_dir=clips, out_dir=out_dir, hardlink=False)

    assert wavs_dir.exists()
    assert (wavs_dir / wav1.name).exists()

    content = meta.read_text(encoding="utf-8").strip().splitlines()
    assert content == [f"wavs/{wav1.name}|こんにちは|こんにちは"]


def test_build_dataset_errors_if_no_pairs(tmp_path: Path) -> None:
    clips = tmp_path / "clips"
    clips.mkdir()
    (clips / "clip.wav").write_bytes(b"RIFF....")

    with pytest.raises(ValueError):
        build_ljspeech_dataset(clips_dir=clips, out_dir=tmp_path / "out")
