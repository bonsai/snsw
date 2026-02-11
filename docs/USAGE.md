# Docker 環境での実行ガイド

このプロジェクトを Docker 環境で実行するためのガイドです。GPU を使用して高速に音声合成・変換を行うことができます。

## 前提条件

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) または Docker Engine がインストールされていること。
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) がインストールされていること（GPU を使用する場合）。

## クイックスタート

### 1. イメージのビルド

```bash
docker-compose build
```

### 2. 推論の実行

`docker-compose run` を使用して、コンテナ内で推論スクリプトを実行します。

```bash
docker-compose run snsw-ai --text "えー、お馴染みの一席でございます。" --speaker_wav data/ref_shinsho.wav --output outputs/docker_out.wav
```

## Tips

- **モデルの永続化**: モデルデータは Docker ボリューム `snsw-models` に保存されるため、コンテナを削除しても再ダウンロードは不要です。
- **GPU の確認**: コンテナ内で `nvidia-smi` を実行して GPU が認識されているか確認できます。
  ```bash
  docker-compose run snsw-ai nvidia-smi
  ```

## Windows (PowerShell) での実行例

```powershell
docker-compose run snsw-ai `
    --text "志ん生でございます。" `
    --speaker_wav "data/ref_shinsho.wav" `
    --output "outputs/docker_out.wav"
```
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

**注意:** `train_xtts_lora.py` はLoRA学習のテンプレートです。実際の学習ループは実装されていません。使用する前に、スクリプトを編集して学習処理を実装する必要があります。

学習処理を実装した後、以下のコマンドでスクリプトを実行します。

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
# XTTS-v2 × RVC ハイブリッド構成ガイド

志ん生さんの声を再現するために、**「話し方（XTTS-v2）」**と**「声質（RVC）」**を分担させる最強の構成案です。

## 1. 役割分担

| モデル | 担当する要素 | LoRA/学習の目的 |
| :--- | :--- | :--- |
| **XTTS-v2** | 独特の「間」、抑揚、江戸弁のイントネーション | 志ん生さん特有の語り口（リズム）を覚えさせる |
| **RVC** | 声の枯れ具合、質感、倍音成分 | 生成された音声を「志ん生さんの喉」を通したような音にする |

## 2. XTTS-v2 への LoRA 適用ポイント

XTTS-v2 の GPT モデル部分に対して LoRA を適用します。

- **ターゲットモジュール**: `attn.q_proj`, `attn.v_proj` などの Attention 層を狙うのが一般的です。
- **Rank (r)**: 8〜16 程度から開始し、話し方の再現度が足りない場合は上げてください。
- **データセット**: 志ん生さんのクリアな語り（30分〜2時間程度）と、正確な文字起こしが必要です。

## 3. RVC との連携フロー

1.  **XTTS 推論**: 
    - LoRA 適用済みの XTTS で音声を生成します。
    - この時点では「話し方は似ているが、声質が少しクリアすぎる」状態を目指します。
2.  **RVC 変換**:
    - XTTS の出力を RVC モデル（志ん生さんの声で学習済み）に入力します。
    - RVC の `index` ファイルを適切に使用することで、より本人に近い質感になります。

## 4. 実装のヒント

添付の `xtts_rvc_hybrid_example.py` は、これらのモデルをプログラムからどう扱うかの骨組みを示しています。

- **学習時**: XTTS-v2 のファインチューニングには `coqui-ai/TTS` の `Trainer` クラスを使用するのが最も安定します。
- **推論時**: 生成した WAV ファイルを一時保存し、それを RVC の CLI や API に渡すパイプラインを組むのが簡単です。

---
この構成により、単一モデルでは到達できない「志ん生さんらしさ」を追求することが可能になります。
# How to Use - Kaggle One-Click Training

## 1. セットアップ
KaggleでGPUを有効にし、最初のセルで以下を実行：

```python
!rm -rf snsw
!git clone https://github.com/bonsai/snsw.git
!python snsw/kaggle_one_click_train.py
```
