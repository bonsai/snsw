# POC (Proof of Concept) - Qwen Voice Clone

## 概要

このフォルダには、Qwen ASR + TTS を使用した音声クローニングの概念実証（POC）が含まれています。

## ファイル

- `qwen_voice_clone_poc.ipynb` - Google Colab で実行可能な Jupyter ノートブック

## 使い方

### Google Colab で実行

1. Google Colab にアクセス: https://colab.research.google.com/
2. `qwen_voice_clone_poc.ipynb` をアップロード
3. ランタイムタイプを GPU に設定（推奨）
4. セルを順番に実行

### ワークフロー

```
1. 環境セットアップ
   ↓
2. Qwen ASR Loader
   - 7秒の元音声を読み込み
   - 文字起こし＋話者特徴を抽出
   ↓
3. 音声プレビュー
   - 元の声をそのまま確認
   ↓
4. テキスト入力
   - 読ませたい文章を入力
   ↓
5. Qwen TTS / Voice Clone
   - ASRで取った「話し方」を条件に
   - 新しいテキストを音声生成
   ↓
6. オーディオ出力
   - 30秒くらいの生成音声を再生
   - ダウンロード可能
```

## 現在の実装状態

### ✓ 実装済み
- 音声アップロードと読み込み
- 音声プレビュー機能
- テキスト入力UI（ipywidgets）
- 音声生成フロー（ダミー実装）
- 生成音声の再生とダウンロード

### 🚧 今後の実装
- Qwen ASR モデルの統合
- Qwen TTS モデルの統合
- 実際の話者特徴抽出
- 実際の音声生成処理

## 注意事項

- 現在はダミー実装です
- 実際のモデルを使用するには、Qwen ASR/TTS のモデルファイルとライブラリが必要です
- GPU 環境での実行を推奨します
