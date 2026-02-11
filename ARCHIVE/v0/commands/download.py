from __future__ import annotations

from pathlib import Path

import typer

from snsw.console import console
from snsw.util import ensure_dir

app = typer.Typer(no_args_is_help=True)


@app.command(help="Download audio/video via yt-dlp (programmatic).")
def youtube(
    url: str = typer.Argument(..., help="YouTube (or supported site) URL"),
    out_dir: Path = typer.Option(Path("data/raw"), help="Output directory"),
    filename: str = typer.Option("%(title)s.%(ext)s", help="yt-dlp output template"),
    format: str = typer.Option("bestaudio/best", help="yt-dlp format selector"),
) -> None:
    ensure_dir(out_dir)

    try:
        from yt_dlp import YoutubeDL  # type: ignore
    except Exception as e:  # pragma: no cover
        raise typer.Exit(code=2) from e

    console.print(f"[bold]Downloading[/bold] {url}")
    ydl_opts = {
        "format": format,
        "outtmpl": str(out_dir / filename),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # info can be a dict (single video) or playlist; we set noplaylist so dict is expected
    title = info.get("title") if isinstance(info, dict) else None
    console.print(f"[green]Done[/green]{' - ' + title if title else ''}")
