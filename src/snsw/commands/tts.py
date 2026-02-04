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


@app.command(help="Fine-tune XTTS-v2 model (requires GPU).")
def finetune(
    dataset_path: Path = typer.Argument(
        ...,
        exists=True,
        help="Path to dataset root (must contain metadata.csv and wavs/ directory)",
    ),
    out_dir: Path = typer.Option(Path("models/finetuned"), help="Output directory for model checkpoints"),
    batch_size: int = typer.Option(2, help="Batch size"),
    epochs: int = typer.Option(10, help="Number of epochs"),
    learning_rate: float = typer.Option(5e-6, help="Learning rate"),
    language: str = typer.Option("ja", help="Target language"),
) -> None:
    """
    Fine-tune XTTS-v2 model using the provided dataset.
    This command requires 'TTS' to be installed and a GPU environment.
    """
    ensure_dir(out_dir)

    try:
        from TTS.tts.configs.xtts_config import XttsConfig
        from TTS.tts.models.xtts import XttsArgs, XttsAudioConfig
        from trainer import Trainer, TrainerArgs
    except Exception as e:
        raise MissingDependencyError("Coqui TTS training dependencies not found. pip install -e '.[tts]'") from e

    console.print(f"[bold]Starting Fine-tuning[/bold] with dataset: {dataset_path}")

    # Note: This is a simplified setup. Real XTTS fine-tuning is complex.
    # We generate a minimal config to get started.
    
    # Check for metadata.csv
    metadata_csv = dataset_path / "metadata.csv"
    if not metadata_csv.exists():
        console.print(f"[red]Error:[/red] metadata.csv not found in {dataset_path}")
        raise typer.Exit(code=1)

    # 1. Prepare dataset JSON for XTTS
    console.print("[bold]Preparing dataset JSON...[/bold]")
    import csv
    import json
    
    items = []
    wavs_dir = dataset_path / "wavs"
    with metadata_csv.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="|")
        for row in reader:
            # LJSpeech format: rel_path|text|norm_text
            if len(row) < 2:
                continue
            rel_path, text = row[0], row[1]
            # Resolve absolute path or keep relative if trainer supports it. 
            # Usually absolute is safer.
            wav_path = (dataset_path / rel_path).resolve()
            if not wav_path.is_relative_to(dataset_path.resolve()):
                continue
            if not wav_path.exists():
                continue
                
            items.append({
                "text": text,
                "audio_file": str(wav_path.absolute()),
                "speaker_name": "Shinsho",
                "language": language
            })

    # Split into train/eval (simple split)
    from random import shuffle
    shuffle(items)
    split_idx = int(len(items) * 0.95)
    train_items = items[:split_idx]
    eval_items = items[split_idx:]

    train_json = out_dir / "dataset_train.json"
    eval_json = out_dir / "dataset_eval.json"
    
    train_json.write_text(json.dumps(train_items, indent=2, ensure_ascii=False), encoding="utf-8")
    eval_json.write_text(json.dumps(eval_items, indent=2, ensure_ascii=False), encoding="utf-8")
    
    console.print(f"Created {train_json} ({len(train_items)} items)")
    console.print(f"Created {eval_json} ({len(eval_items)} items)")

    # 2. Config and Training (Placeholder)
    # Ideally, we would load a base config and override it.
    console.print("[yellow]Warning:[/yellow] Actual training execution is not fully automated yet.")
    console.print("To run training, please use the generated JSON files with the standard XTTS recipe.")
    console.print(f"Output directory: {out_dir}")

    
    # In a real implementation, we would instatiate the Trainer here.
    # For now, we will output the command that user might want to run or a message.
    console.print("\n[bold]Recommended Action:[/bold]")
    console.print("Please use the official XTTS fine-tuning script or WebUI for best results.")
    console.print("If you wish to proceed programmatically, please ensure you have the base model downloaded.")
