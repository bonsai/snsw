from __future__ import annotations

import typer

from snsw.commands.audio import app as audio_app
from snsw.commands.dataset import app as dataset_app
from snsw.commands.download import app as download_app
from snsw.commands.rvc import app as rvc_app
from snsw.commands.transcribe import app as transcribe_app
from snsw.commands.tts import app as tts_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(download_app, name="download")
app.add_typer(audio_app, name="audio")
app.add_typer(transcribe_app, name="transcribe")
app.add_typer(dataset_app, name="dataset")
app.add_typer(tts_app, name="tts")
app.add_typer(rvc_app, name="rvc")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
