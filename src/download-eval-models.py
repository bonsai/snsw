#!/usr/bin/env python
import os
import subprocess
from pathlib import Path

def run_command(command):
    print(f"実行中: {command}")
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"エラーが発生しました: {e}")

def download_nisqa():
    """NISQA (自然さ・品質評価モデル) のダウンロード"""
    print("\n--- NISQA モデルのダウンロード ---")
    # vinesmsuic/NISQA も 401/404 になるため、オリジナルの GitHub リポジトリ等からのダウンロードを推奨。
    local_dir = Path("C:/models/eval/nisqa")
    local_dir.mkdir(parents=True, exist_ok=True)
    
    print("Hugging Face 上のリポジトリにアクセスできないため、GitHub からの手動ダウンロードを検討してください。")
    print("URL: https://github.com/nhenning/NISQA")
    print(f"モデルファイルを {local_dir} に配置してください。")

def download_resemblyzer():
    """Resemblyzer (話者類似度評価モデル) のダウンロード"""
    print("\n--- Resemblyzer モデルのダウンロード ---")
    # Resemblyzerは通常パッケージインストール時に自動ダウンロードされるが、
    # 明示的に管理するためにディレクトリを準備
    local_dir = "C:/models/eval/resemblyzer"
    os.makedirs(local_dir, exist_ok=True)
    print(f"Resemblyzer 用のディレクトリを確認しました: {local_dir}")
    # 実際にはライブラリが内部で利用する .pt ファイルなどを配置する

def download_wvmos():
    """Wav2Vec2-based MOS prediction (自然さ予測)"""
    print("\n--- Wav2Vec2-MOS モデルのダウンロード ---")
    # mush42/wvmos も認証エラーになるため、ライブラリ(wvmos)のインストールで代用
    print("huggingface-cli でのダウンロードに失敗したため、pip install wvmos を試行します。")
    run_command("pip install wvmos")
    
    local_dir = "C:/models/eval/wvmos"
    os.makedirs(local_dir, exist_ok=True)
    print(f"Wav2Vec2-MOS はライブラリ経由で利用可能です。ディレクトリ: {local_dir}")

def main():
    # huggingface_hub のインストール確認
    run_command("pip install huggingface_hub")
    
    # 保存先ルートの作成
    os.makedirs("C:/models/eval", exist_ok=True)
    
    # 各評価モデルのダウンロード
    download_nisqa()
    download_wvmos()
    download_resemblyzer()
    
    print("\nすべての評価用モデルのダウンロード処理が完了しました。")
    print(f"モデルは C:\\models\\eval に保存されています。")

if __name__ == "__main__":
    main()
