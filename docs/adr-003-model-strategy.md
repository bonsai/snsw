# ADR-003: 使用モデルの戦略的明示

このプロジェクトで正式に使用するモデルを明示します。基本構成は「TTSで音声生成」→「VCで質感変換」のハイブリッド方式です。

## 音声合成 (TTS)
- **Coqui XTTS-v2**
  - 目的: テキストから志ん生風の音声を生成
  - 備考: 少量の参照音声でも高品質なゼロショットが可能。必要に応じてファインチューニングを行う
- **GPT-SoVITS**
  - 目的: 少量の学習データで強力なボイスクローンを実現（特に日本語に強い）
  - 保存先: `C:/models/TTS/gpt-sovits`
- **Fish-Speech**
  - 目的: SOTA（最先端）な音声生成エンジンの検証
  - 保存先: `C:/models/TTS/fish-speech`
- **StyleTTS2**
  - 目的: 高速かつ高品質な音声合成の検証
  - 保存先: `C:/models/TTS/styletts2`

## 声質変換 (VC)
- 名称: RVC (Retrieval-based Voice Conversion)
- 目的: XTTSで生成した音声を志ん生の声質へ近づける質感変換
- 備考: 「枯れ声」やニュアンスの補強に使用

## 文字起こし
- 名称: Whisper (large-v3)
- 目的: 学習用データセット作成のための高精度なトランスクリプト生成
- 備考: 自動生成後に手修正を推奨

## 評価モデル
- **NISQA (v2)**
  - 目的: 音声の自然さ、歪み、ノイズなどの品質を多角的にスコアリング
  - 保存先: `C:/models/eval/nisqa`
- **Wav2Vec2-MOS (wvmos)**
  - 目的: AIによるMOS（Mean Opinion Score）の自動予測
  - 保存先: `C:/models/eval/wvmos`
- **Resemblyzer**
  - 目的: 話者エンベディングによる話者類似度の算出
  - 保存先: `C:/models/eval/resemblyzer`

## 参照
- ワークフロー: docs/ENV.md
- 技術スタック: docs/STAC.md
- 設計判断: docs/ADR.md
