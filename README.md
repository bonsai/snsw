# 五代目古今亭志ん生 音声再現プロジェクト (SNSW)

五代目古今亭志ん生の音声を XTTS-v2 および RVC を用いて再現するためのツールキットです。
Kaggle 環境でのトレーニング、および Docker を用いたローカル/クラウド運用に最適化されています。

## 🚀 クイックスタート (Docker)

Docker を使用して、依存関係のインストールなしに即座に推論やトレーニングを開始できます。

### 1. 準備
```bash
docker-compose build
```

### 2. 推論の実行
```bash
docker-compose run --rm snsw-ai python src/kaggle/run_inference.py --input_audio /app/audio-source/001.wav
```

### 3. 自動文字起こし & トレーニング
YouTube URL から音声を抽出し、自動で文字起こしして LoRA 学習を行います。
```bash
docker-compose run --rm snsw-ai python v4/kaggle_one_click_train.py
```

## 📁 ディレクトリ構成

- `src/`: 共通ソースコード（Kaggle/LoRA/Tools）
- `docs/`: プロジェクトドキュメント
  - `ADR.md`: 設計決定記録
  - `USAGE.md`: 詳細な利用方法
  - `UX.md`: ワークフローとユーザー体験設計
  - `README.md`: 内部詳細説明
- `v4/`: 以前のバージョンのスクリプトアーカイブ
- `data/`: 学習・推論データ（ボリュームマウント）
- `tts_outputs/`: 生成音声の出力先

## 📖 詳細ドキュメント

より詳細な情報は `docs/` ディレクトリ内の各ファイルを参照してください。
- [利用ガイド](docs/USAGE.md)
- [設計思想](docs/ADR.md)
- [開発ロードマップ](docs/UX.md)

---
Developed by Manus AI & bonsai
