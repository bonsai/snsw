# ADR-014: 追加学習（Fine-tuning）の実行戦略とモデル保存

## 1. ステータス
**提案中 (Proposed)**

## 2. コンテキスト
「出世魚プロジェクト」では、ゼロショット生成から始まり、段階的に精度を高めていく。このプロセスにおいて、いつ学習を行い、どのパラメータを優先し、どのようにモデルを保存・切り替えるかの戦略が必要である。

## 3. 決定事項

### 3.1 学習のトリガー
[eval-batch-stats.py](../src/eval-batch-stats.py) のレポートに基づき、以下の基準で学習を実行する。
- **話者類似度スコア < 0.7**: 優先的に Fine-tuning (LoRA等) を実施。
- **MOSスコア < 3.0**: データセットのクリーニング後に学習率を下げて再学習。

### 3.2 学習フェーズの定義
1.  **Phase 1 (Quick Adaptation)**: XTTS v2 の LoRA 学習（少量の高品質データ）。
2.  **Phase 2 (Deep Learning)**: GPT-SoVITS または Fish-Speech のフル Fine-tuning（大量データ）。
3.  **Phase 3 (Refinement)**: RVC モデルの追加学習による「声質」の最終調整。

### 3.3 チェックポイントとアーティファクト管理
学習済みの重みファイルは `MODELS/trained/` 配下にモデル名・日付・評価スコアを含めた形式で保存する。

```text
MODELS/trained/
└── [model_name]_[version]_[YYYYMMDD]_[score]/
    ├── weights.pth
    ├── config.json
    └── evaluation_report.md
```

### 3.4 学習の効率化 (GPU Resource Management)
- 大規模学習は Docker コンテナ経由で実行し、メモリ制限や VRAM 管理を最適化する。
- 学習中断時からのレジューム（Resume Training）を常に有効にする。

## 4. 決定による影響

### メリット
- **段階的な品質向上**: 一気に完璧を目指さず、フェーズごとに成果を確認できる。
- **資産の蓄積**: 過去の学習済みモデルがスコア付きで保存されるため、最良のモデルにいつでも戻れる。

### デメリット
- **管理コスト**: 多数のチェックポイントが生成されるため、定期的なクリーンアップが必要。
- **複雑性**: 複数の学習手法（LoRA, Full FT, RVC）を併用するため、習得コストが高い。

## 5. 補足
本戦略は、[mlops.yml](../.github/workflows/mlops.yml) における `train-common-run.py` の実行ロジックの指針となる。
