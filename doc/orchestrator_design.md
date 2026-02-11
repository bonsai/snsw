# ファイルオーケストレーター設計: 出世魚ループ

## 1. エージェント進化（出世魚）の定義
ループの各段階を以下の名称で管理します。

| 段階 (Iteration) | 出世魚名 | 役割/状態 |
| :--- | :--- | :--- |
| **v1** | **WAKASHI (ワカシ)** | 初期生成・ベースライン |
| **v2** | **INADA (イナダ)** | 診断に基づく第一次改善 |
| **v3** | **WARASA (ワラサ)** | 高度なパラメータ調整・第二次改善 |
| **Final** | **BURI (ブリ)** | 最終完成形（最新コード） |

## 2. ファイル命名規則 (outputフォルダ)
全ての成果物を `/home/ubuntu/output/` (Colabでは `/content/drive/MyDrive/VC/output/`) に集約します。

- **WAV**: `{rank}_audio.wav`
- **Code**: `{rank}_code.py`
- **Report**: `{rank}_report.json`
- **Summary**: `shusseuo_ledger.md` (出世魚台帳)

## 3. オーケストレーターの責務
1.  現在のランク（魚名）を決定
2.  TTSコードを実行し、`{rank}_audio.wav` を保存
3.  診断を実行し、`{rank}_report.json` を保存
4.  改善案を練り、次回のランク用の `{rank}_code.py` を生成
5.  最後に `BURI_final_code.py` を出力
