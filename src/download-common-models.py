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

def download_gpt_sovits():
    print("\n--- GPT-SoVITS モデルのダウンロード ---")
    repo_id = "lj1995/GPT-SoVITS"
    local_dir = "C:/models/gpt-sovits"
    # 'huggingface-cli download' は非推奨のため 'hf download' を検討（環境による）
    # ここでは確実に動作する既存コマンドを維持しつつ、パスを確認
    run_command(f"huggingface-cli download {repo_id} --local-dir {local_dir}")

def download_fish_speech():
    print("\n--- Fish-Speech モデルのダウンロード ---")
    repo_id = "fishaudio/fish-speech-1.4"
    local_dir = "C:/models/fish-speech"
    run_command(f"huggingface-cli download {repo_id} --local-dir {local_dir}")

def download_styletts2():
    print("\n--- StyleTTS2 モデルのダウンロード ---")
    repo_id = "yl4579/StyleTTS2-LibriTTS"
    local_dir = "C:/models/styletts2"
    run_command(f"huggingface-cli download {repo_id} --local-dir {local_dir}")

def main():
    # huggingface_hub のインストール確認とインストール
    print("huggingface_hub をチェック中...")
    run_command("pip install huggingface_hub")
    
    # 各モデルのダウンロード
    download_gpt_sovits()
    download_fish_speech()
    download_styletts2()
    
    print("\nすべてのモデルのダウンロード処理が完了しました。")
    print(f"モデルは C:\\models に保存されています。")

if __name__ == "__main__":
    main()
