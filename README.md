# SNSW Project: 五代目古今亭志ん生 音声再現システム

## 概要

本プロジェクトは、伝説的な落語家「五代目古今亭志ん生」の声を、最新のAI技術（TTS/VC）を用いて現代に蘇らせることを目的とした、マルチモデル音声生成・評価システムです。単一のモデルに依存せず、複数のSOTA（State-of-the-Art）モデルを並行して検証し、独自の評価ループ（LOOP）とオーケストレーター（出世魚）によって、最高品質の音声を追求します。

## プロジェクトの核心

1.  **マルチモデルTTS・クローニング:** XTTS v2, GPT-SoVITS, Fish-Speech, StyleTTS2, Qwen2-Audio等の複数の強力なエンジンを搭載。
2.  **ハイブリッド再現:** TTSによる音声生成と、RVCによる質感変換を組み合わせた独自の再現フロー。
3.  **音声品質改善ループ (LOOP):** AIエージェント（Inspector/Diagnostician/Strategist）が生成音声を診断し、改善策を自動立案。
4.  **科学的評価:** MOS予測、話者類似度、物理特性解析に基づいた数値によるモデル選定と学習判断。

## 主要ディレクトリ構成

- `src/`: システムのコアロジック、各TTSモデルの実行スクリプト、評価ツール群。
- `docs/`: アーキテクチャ決定記録（ADR）、設計仕様、学習計画。
- `SOURCE/`: 学習・生成の元となる志ん生の音声データおよびテキストデータ。
- `tts_outputs/`: 生成された音声と、それに対する評価レポート。
- `models/`: 各AIモデルの重みファイル（ホスト側の `C:\models` と共有）。

## クイックスタート (Docker)

```bash
# コンテナのビルドと起動
docker-compose up -d --build

# テキスト読み上げの実行 (例: XTTS v2)
docker exec snsw-ai-container python3 src/tts-multi-selector.py

# 全生成音声の一括評価と統計レポート作成
docker exec snsw-ai-container python3 src/eval-batch-stats.py
```

## 意思決定の記録 (ADR)

プロジェクトの詳細な設計判断については、`docs/adr-000-index.md` を参照してください。
- [ADR-001: 技術スタックの選定](docs/adr-001-tech-stack.md)
- [ADR-005: 音声品質改善ループ (LOOP) の設計](docs/adr-005-quality-loop-design.md)
- [ADR-010: モデル評価基準と学習継続・見切りの判断指針](docs/adr-010-model-evaluation-criteria.md)
