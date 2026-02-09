import sys
import os
import json
import time
from pathlib import Path
import argparse
from datetime import datetime

# --- Kaggle Environment Path Setup ---
KAGGLE_WORKING = Path("/kaggle/working")
PROJECT_ROOT = KAGGLE_WORKING / "snsw"
DATA_ROOT = KAGGLE_WORKING / "data"

current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

try:
    from trainer import Trainer, TrainerArgs
    from TTS.config.shared_configs import BaseDatasetConfig
    from TTS.tts.datasets import load_tts_samples
    from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig, XttsAudioConfig
    from peft import LoraConfig, get_peft_model
except ImportError as e:
    print(f"Error importing libraries: {e}")

def generate_report(output_dir, stats):
    """学習結果のレポートを生成する"""
    report_path = Path(output_dir) / "training_report.md"
    
    report_content = f"""# XTTS LoRA Training Report
Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- **Status**: Success ✅
- **Duration**: {stats.get('duration', 'N/A')}
- **Epochs**: {stats.get('epochs', 'N/A')}
- **Batch Size**: {stats.get('batch_size', 'N/A')}

## Training Stats
- **Train Samples**: {stats.get('train_samples', 'N/A')}
- **Eval Samples**: {stats.get('eval_samples', 'N/A')}
- **Trainable Parameters**: {stats.get('trainable_params', 'N/A')}

## Output Locations
- **LoRA Adapter**: `{stats.get('lora_path', 'N/A')}`
- **Config**: `{stats.get('config_path', 'N/A')}`

## Environment
- **Project Root**: `{PROJECT_ROOT}`
- **Dataset**: `{stats.get('dataset_path', 'N/A')}`
"""
    with open(report_path, "w") as f:
        f.write(report_content)
    
    # JSON形式でも保存
    json_path = Path(output_dir) / "training_stats.json"
    with open(json_path, "w") as f:
        json.dump(stats, f, indent=4)
        
    print(f"Report generated: {report_path}")

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description="XTTS LoRA Training for Kaggle")
    parser.add_argument("--dataset_path", type=str, default=str(DATA_ROOT / "metadata.csv"), help="Path to metadata.csv")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs")
    args = parser.parse_args()

    PRETRAINED_MODEL_ROOT = PROJECT_ROOT / "pretrained_model"
    if not PRETRAINED_MODEL_ROOT.exists():
        PRETRAINED_MODEL_ROOT = current_dir / "pretrained_model"
        
    MYTTSDATASET_ROOT = DATA_ROOT
    SPEAKER_REFERENCE_ROOT = PROJECT_ROOT / "speaker_reference"
    OUTPUT_ROOT_DIR = PROJECT_ROOT / "training_output"

    XTTS_MEL_PATH = PRETRAINED_MODEL_ROOT / "mel_stats.pth"
    XTTS_DVAE_PATH = PRETRAINED_MODEL_ROOT / "dvae.pth"
    XTTS_MODEL_PATH = PRETRAINED_MODEL_ROOT / "model.pth"
    XTTS_TOKENIZER_PATH = PRETRAINED_MODEL_ROOT / "vocab.json"
    
    SPEAKER_REFERENCE_WAV_PATH = SPEAKER_REFERENCE_ROOT / "reference.wav"
    if not SPEAKER_REFERENCE_WAV_PATH.exists():
        SPEAKER_REFERENCE_WAV_PATH = current_dir / "audio-source" / "001.wav"

    OUTPUT_PATH = OUTPUT_ROOT_DIR / "checkpoints"
    LORA_ADAPTER_PATH = OUTPUT_PATH / "lora_adapter"
    XTTS_LORA_ORIGINAL_CONFIG_PATH = LORA_ADAPTER_PATH / "original_xtts_config.json"

    config_dataset = BaseDatasetConfig(
        formatter="ljspeech",
        dataset_name="ljspeech",
        path=str(MYTTSDATASET_ROOT),
        meta_file_train=args.dataset_path,
        language="ja",
    )

    DATASETS_CONFIG_LIST = [config_dataset]
    train_samples, eval_samples = load_tts_samples(
        DATASETS_CONFIG_LIST,
        eval_split=True,
        eval_split_max_size=256,
        eval_split_size=0.05,
    )

    model_args = GPTArgs(
        max_conditioning_length=132300,
        min_conditioning_length=66150,
        debug_loading_failures=False,
        max_wav_length=255995,
        max_text_length=200,
        mel_norm_file=str(XTTS_MEL_PATH),
        dvae_checkpoint=str(XTTS_DVAE_PATH),
        xtts_checkpoint=str(XTTS_MODEL_PATH),
        tokenizer_file=str(XTTS_TOKENIZER_PATH),
        gpt_num_audio_tokens=1026,
        gpt_start_audio_token=1024,
        gpt_stop_audio_token=1025,
        gpt_use_masking_gt_prompt_approach=True,
        gpt_use_perceiver_resampler=True,
    )

    audio_config = XttsAudioConfig(
        sample_rate=22050,
        dvae_sample_rate=22050,
        output_sample_rate=24000
    )

    config = GPTTrainerConfig(
        output_path=str(OUTPUT_PATH),
        model_args=model_args,
        run_name="xtts_lora_kaggle",
        project_name="snsw_lora",
        run_description="LoRA fine-tuning on Kaggle",
        dashboard_logger="tensorboard",
        audio=audio_config,
        batch_size=2,
        batch_group_size=48,
        eval_batch_size=1,
        num_loader_workers=2,
        epochs=args.epochs,
        print_step=10,
        save_step=1000,
        optimizer="AdamW",
        lr=1e-5,
    )

    model_peft = GPTTrainer.init_from_config(config)
    
    peft_config = LoraConfig(
        inference_mode=False,
        r=8,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["c_attn", "c_proj", "c_fc"],
    )
    model_peft.xtts.gpt = get_peft_model(model_peft.xtts.gpt, peft_config)
    trainable_params, _ = model_peft.xtts.gpt.get_nb_trainable_parameters()

    trainer_args = TrainerArgs(
        restore_path=None,
        skip_train_epoch=False,
        start_with_eval=True,
        grad_accum_steps=64,
    )
    
    trainer = Trainer(
        args=trainer_args,
        config=config,
        output_path=str(OUTPUT_PATH),
        model=model_peft,
        train_samples=train_samples,
        eval_samples=eval_samples,
    )

    trainer.fit()

    os.makedirs(LORA_ADAPTER_PATH, exist_ok=True)
    model_peft.xtts.gpt.save_pretrained(str(LORA_ADAPTER_PATH))
    config.save_json(str(XTTS_LORA_ORIGINAL_CONFIG_PATH))

    # レポート用の統計情報を収集
    end_time = time.time()
    duration = end_time - start_time
    stats = {
        "duration": f"{duration:.2f} seconds",
        "epochs": args.epochs,
        "batch_size": config.batch_size,
        "train_samples": len(train_samples),
        "eval_samples": len(eval_samples),
        "trainable_params": trainable_params,
        "lora_path": str(LORA_ADAPTER_PATH),
        "config_path": str(XTTS_LORA_ORIGINAL_CONFIG_PATH),
        "dataset_path": args.dataset_path
    }
    
    generate_report(OUTPUT_ROOT_DIR, stats)
    print(f"Success! LoRA saved to {LORA_ADAPTER_PATH}")

if __name__ == "__main__":
    main()
