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
