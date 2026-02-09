# How to Use - Kaggle One-Click Training

このドキュメントでは、Kaggle Notebook を使用して「1クリック」で五代目古今亭志ん生の LoRA 学習を完了させる手順を説明します。

## 1. Kaggle Notebook の作成
1. [Kaggle](https://www.kaggle.com/) にログインし、**"New Notebook"** をクリックします。
2. 右側のパネルで以下を設定します：
   - **Accelerator**: `GPU P100` (学習に最適)
   - **Internet**: `On` (必須)

## 2. 学習の実行（1クリック）
最初のセルに以下のコードを貼り付けて実行（Ctrl+Enter）してください。

```python
# 1. リポジトリをクローン
!git clone https://github.com/bonsai/snsw.git
%cd snsw

# 2. 全自動学習スクリプトを実行
!python kaggle_one_click_train.py
```

## 3. 処理内容
このスクリプトを実行すると、内部で以下の処理が自動的に行われます：
- **環境構築**: `TTS`, `peft` などの必要なライブラリのインストール。
- **データ準備**: 元データURLからのダウンロードと、学習用メタデータの構築。
- **LoRA学習**: XTTS-v2 モデルへの LoRA 適用とファインチューニング。
- **ログ保存**: すべての実行ログ（エラー含む）を `dev/` ディレクトリに保存。

## 4. 学習結果の確認
学習が完了すると、以下の場所に成果物が出力されます：
- **LoRA重み**: `/kaggle/working/outputs/xtts_lora/lora_weights`
- **ログファイル**: `/kaggle/working/snsw/dev/`

## 5. エラーが発生した場合
`/kaggle/working/snsw/dev/` 内の最新の `.log` ファイルを確認してください。エラーの詳細はすべてここに記録されています。

---
## 元データについて
本プロジェクトでは、以下の公開アーカイブ音源を学習のベースとして推奨しています。
- **元データURL例**: [Internet Archive - 五代目古今亭志ん生](https://archive.org/details/shinsho_sample)
- **データセットの作り方**: 音声を 5-10 秒に分割し、`metadata.csv` に `ファイル名|テキスト|話者名` の形式で記述します。
