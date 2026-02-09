import os
import subprocess
import sys

def install_dependencies():
    """Kaggle環境に必要なライブラリをインストールする"""
    print("--- Step 1: Installing system dependencies ---")
    # KaggleはDebianベースなのでapt-getを使用
    subprocess.run(["apt-get", "update"], check=True)
    subprocess.run(["apt-get", "install", "-y", "ffmpeg", "libsndfile1"], check=True)

    print("\n--- Step 2: Installing Python libraries ---")
    # 音声合成とLoRAに必要なライブラリ
    libs = [
        "TTS",
        "peft",
        "transformers",
        "datasets",
        "safetensors",
        "librosa",
        "scipy"
    ]
    subprocess.run([sys.executable, "-m", "pip", "install", "-U"] + libs, check=True)
    print("\nInstallation completed successfully!")

def setup_project():
    """リポジトリのクローンとディレクトリ作成（Kaggle作業用）"""
    print("\n--- Step 3: Setting up project directories ---")
    if not os.path.exists("snsw"):
        subprocess.run(["git", "clone", "https://github.com/bonsai/snsw.git"], check=True)
    
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("models/rvc", exist_ok=True)
    print("Project setup completed!")

if __name__ == "__main__":
    # Kaggle環境かどうかを簡易チェック
    if os.path.exists("/kaggle/working"):
        install_dependencies()
        setup_project()
    else:
        print("This script is intended to run on Kaggle. Skipping installation.")
