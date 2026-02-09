# Kaggle 実行ガイド

Kaggle Notebooks の GPU 環境を使用して音声合成・変換を行うためのガイドです。

## 準備

1.  Kaggle で新しい Notebook を作成します。
2.  右側の **Settings** パネルで以下を設定します：
    - **Accelerator**: `GPU P100` または `GPU T4 x2`
    - **Internet**: `On`

## 実行手順

### 1. セットアップ

最初のセルに以下のコードを貼り付けて実行し、環境を構築します。

```python
import os
import subprocess

# セットアップスクリプトの取得と実行
!curl -O https://raw.githubusercontent.com/bonsai/snsw/main/kaggle_setup.py
import kaggle_setup
kaggle_setup.install_dependencies()
kaggle_setup.setup_project()
```

### 2. 推論の実行

次のセルで、`hybrid_inference.py` を呼び出して音声を生成します。

```python
%cd /kaggle/working/snsw

!python hybrid_inference.py \
    --text "えー、お馴染みの一席でございます。" \
    --speaker_wav "data/ref_shinsho.wav" \
    --output "/kaggle/working/outputs/final_voice.wav"
```

## 注意点

- **保存先**: `/kaggle/working` 以下のファイルはセッション終了後も保存（Save Version時）されますが、`/tmp` などは消去されます。
- **GPU制限**: Kaggle の GPU 使用時間枠（週30時間程度）に注意してください。
- **モデルのアップロード**: RVCモデルやLoRA重みは、Kaggle の **Datasets** としてアップロードしてマウントすると、毎回ダウンロードせずに済みます。

## LoRA 学習の実行

Kaggle の GPU を使用して XTTS-v2 の LoRA 学習を行う手順です。

### 1. データの準備
学習データ（WAVファイルと `metadata.csv`）を Kaggle Dataset としてアップロードし、ノートブックにマウントします。
`metadata.csv` は以下の形式（LJSpeech互換）を想定しています：
`audio_file_name|text|speaker_name`

### 2. 学習スクリプトの実行

```python
!python train_xtts_lora.py \
    --dataset_path "/kaggle/input/your-dataset-name/metadata.csv" \
    --output_dir "/kaggle/working/outputs/xtts_lora_shinsho" \
    --epochs 10 \
    --batch_size 2 \
    --grad_accum 4
```

### 3. パラメータの調整
- **batch_size**: VRAM不足（OOM）が出る場合は 1 に下げてください。
- **grad_accum**: 実質的なバッチサイズを維持するために、`batch_size * grad_accum` が一定になるよう調整します。
- **lora_r / lora_alpha**: 話し方の再現度が低い場合は値を大きく（例: r=32, alpha=64）してみてください。
