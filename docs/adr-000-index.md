# Architecture Decision Records (ADR) Index

このディレクトリには、プロジェクトの主要な技術選定、設計方針、および意思決定の記録が時系列順に保存されています。

## ADR一覧

- **[ADR-001: 技術スタックの選定](adr-001-tech-stack.md)**
  - XTTS-v2 と RVC を組み合わせたハイブリッド構成の採用について。
- **[ADR-002: 実行・学習環境の定義](adr-002-environment.md)**
  - 推奨スペック、音声データ形式、ツール群の定義。
- **[ADR-003: 使用モデルの戦略的明示](adr-003-model-strategy.md)**
  - TTS、VC、評価モデルの具体的な選定と保存方針。
- **[ADR-004: v2ディレクトリ構成の再編](adr-004-v2-reorganization.md)**
  - プロジェクトのスケールに伴うフォルダ構造の最適化。
- **[ADR-005: 音声品質改善ループ (LOOP) の設計](adr-005-quality-loop-design.md)**
  - 診断エージェント・スタックのアーキテクチャ。
- **[ADR-006: ファイルオーケストレーター設計 (出世魚)](adr-006-orchestrator-shusseuo.md)**
  - エージェントの進化プロセスとファイル命名規則。
- **[ADR-007: 機械学習の意思決定プロセス (MLDR)](adr-007-ml-decision-process.md)**
  - ファインチューニングの学習計画と成功基準。
- **[ADR-008: 評価FBに基づく学習計画の動的調整](adr-008-learning-plan.md)**
  - 評価スコアに応じた改善アクションの定義。
- **[ADR-009: スキルの定義と拡張](adr-009-skill-definition.md)**
  - システムが実行可能な具体的なスキル（wav2mp3等）の定義。
- **[ADR-010: モデル評価基準と学習継続・見切りの判断指針](adr-010-model-evaluation-criteria.md)**
- **[ADR-011: TTSモデル選定と複数モデル共存環境の構築](adr-011-tts-model-selection.md)**
- **[ADR-012: 音声品質の自動採点システムの導入](adr-012-audio-scoring.md)**
