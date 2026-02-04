# 五代目古今亭志ん生 音声再現プロジェクト

このプロジェクトは、AI技術（音声合成・声質変換）を用いて、昭和の名人・五代目古今亭志ん生の声を再現することを目的としています。
2026年時点の最新技術トレンドに基づき、**Coqui XTTS-v2** と **RVC (Retrieval-based Voice Conversion)** を組み合わせたハイブリッド手法により、志ん生特有の「枯れた声」や「間」の高品質な再現を目指します。

## 概要

従来の単一モデル（Tortoise TTSなど）ではなく、複数の最新AIモデルを組み合わせることで、以下の要素を再現します。
- **声質**: 晩年の枯れた味わい深い声
- **話し方**: 独特の「間」や抑揚
- **柔軟性**: 任意のテキストからの音声生成

## 技術スタック
### 使用モデル一覧
- [MODELS.md](./docs/MODELS.md) に、正式採用しているモデル（XTTS-v2 / RVC / Whisper large-v3）を明示しています。

### コアモデル
*   **Coqui XTTS-v2**: メインの音声合成エンジン。日本語品質が高く、少量のデータでも高品質なクローニング（ゼロショット）が可能。
*   **RVC (Retrieval-based Voice Conversion)**: 生成された音声の質感をさらに志ん生の声に近づけるための変換モデル。

### データ処理・学習
*   **Whisper (large-v3)**: 学習データの作成に使用する高精度な文字起こしツール。
*   **yt-dlp**: 音源収集ツール。
*   **Audacity / pydub**: 音声編集・ノイズ除去（拍手や笑い声のカット）。

## 推奨環境

高品質な学習（ファインチューニング）を行うためには、以下のハードウェア環境を推奨します。

| 項目 | 推奨スペック | 備考 |
| :--- | :--- | :--- |
| **OS** | Windows / Linux | Pythonが動作する環境 |
| **GPU (VRAM)** | **16GB 〜 24GB 以上** | 本格的な学習に推奨（NVIDIA A100等）。推論のみなら8-12GBでも可。 |
| **ストレージ** | SSD | 十分な空き容量（音声データ・モデル保存用） |

## ワークフロー

1.  **データ収集**: 志ん生の演目から、クリアな音声部分のみを抽出します（推奨：3〜10時間分）。
2.  **前処理**: ノイズ（拍手・笑い声）を除去し、Whisperでテキスト化してデータセットを作成します。
3.  **学習 (Fine-tuning)**:
    *   XTTS-v2を用いてモデルをファインチューニングします。
    *   必要に応じてRVCモデルも学習させます。
4.  **音声生成**: テキストを入力して音声を生成し、RVCで質感を整えます。

## 実装コード（CLI）

このリポジトリには、上記ワークフローをローカルで回すための最小CLI（Python）が含まれます。
学習（ファインチューニング）の本体は `AllTalk TTS` / `xtts-finetune-webui` 等の既存UIを推奨し、本CLIは **データ作成・推論の補助** にフォーカスします。

### 前提

* Python 3.10+
* `ffmpeg`（`pydub` による変換/分割で使用）

### インストール

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"
# Whisper / XTTS を使う場合
pip install -e ".[whisper,tts]"
```

### 使い方（例）

1) ダウンロード（yt-dlp）

```powershell
snsw download youtube "https://www.youtube.com/watch?v=..." --out-dir data/raw
```

2) WAV 化（22050Hz / mono / 16bit）

```powershell
snsw audio to-wav data/raw/input.mp4 --out data/wav/input.wav
```

3) 無音で自動分割

```powershell
snsw audio split-silence data/wav/input.wav --out-dir data/clips
```

4) クリップを文字起こし（Whisper）して `*.txt` を生成

```powershell
snsw transcribe clips data/clips --language ja --model-size large-v3 --out-manifest data/transcripts.jsonl
```

5) `*.txt` を目視で修正（重要）

6) 学習用データセット（LJSpeech 互換）を作成

```powershell
snsw dataset build data/clips --out-dir datasets/shinsho --hardlink
```

7) 推論（XTTS-v2 ゼロショット例）

```powershell
snsw tts clone "今日はいい天気ですね" --speaker-wav data/ref.wav --out-wav outputs/xtts.wav --language ja
```

8) RVC 変換（外部コマンドをテンプレートで実行）

```powershell
snsw rvc convert outputs/xtts.wav --out-wav outputs/rvc.wav --template "python path\\to\\infer_cli.py --model models\\shinsho.pth --input {in} --output {out}"
```

## 権利関係・注意事項

*   **著作権について**: 1950〜60年代の音源を使用する場合、著作権や著作隣接権（レコード会社・放送局など）に十分配慮してください。
*   **利用範囲**: 生成された音声の公開や商用利用には、権利元の許諾が必要となる場合があります。私的利用の範囲内での研究・実験を推奨します。

## 参考資料
詳細は以下のドキュメントを参照してください。
- [MODELS (使用モデル一覧)](./docs/MODELS.md)
- [ADR (Architecture Decision Record)](./docs/ADR.md)
- [ENV (環境構築ガイド)](./docs/ENV.md)
- [STAC (技術スタック比較)](./docs/STAC.md)
