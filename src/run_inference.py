import os
import sys
import subprocess
import logging
import datetime
import traceback
import argparse

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def run_command(cmd, description):
    logger.info(f"Starting: {description}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        logger.info(f"Successfully completed: {description}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error in {description}: {e}")
        raise

def setup_environment():
    """Kaggle環境のセットアップ"""
    logger.info("Setting up environment...")
    
    # 必要なシステムパッケージ
    run_command("apt-get update && apt-get install -y ffmpeg", "Install system dependencies")
    
    # Pythonライブラリ
    # Coqui TTSと依存関係
    # Kaggle環境に合わせてバージョン調整が必要な場合があるが、まずは最新または安定版を指定
    pip_cmd = "pip install --no-cache-dir coqui-tts torch torchaudio transformers"
    run_command(pip_cmd, "Install Python libraries")

def main():
    parser = argparse.ArgumentParser(description="Kaggle TTS Inference Launcher")
    parser.add_argument("--text", type=str, default="これはKaggleでの音声合成テストです。", help="Text to synthesize")
    # デフォルトの参照音声パスは適宜変更してください
    parser.add_argument("--speaker_wav", type=str, default="/kaggle/working/snsw/data/raw/input.wav", help="Reference speaker wav")
    # モデルディレクトリ（デフォルトはXTTSのデフォルトダウンロード先やKaggle Datasetのパスを想定）
    # ここでは仮にカレントディレクトリ直下の models を指定するが、実際には Dataset パスなどを指定する
    parser.add_argument("--model_dir", type=str, default="/kaggle/input/xtts-v2-models", help="Model checkpoint directory")
    parser.add_argument("--output_dir", type=str, default="/kaggle/working/output", help="Output directory")
    
    args = parser.parse_args()
    
    try:
        # 1. 環境セットアップ
        setup_environment()
        
        # 2. 推論スクリプトの実行
        # snsw/src/lora/inference.py を呼び出す
        # 現在のスクリプトの場所から相対パスで指定
        current_dir = os.path.dirname(os.path.abspath(__file__))
        inference_script = os.path.join(current_dir, "..", "lora", "inference.py")
        
        if not os.path.exists(inference_script):
            # リポジトリ構造が変わっている場合のフォールバック（例：snswリポジトリ内）
            inference_script = "/kaggle/working/snsw/src/lora/inference.py"
        
        if not os.path.exists(inference_script):
             raise FileNotFoundError(f"Inference script not found at {inference_script}")

        cmd = (
            f"python {inference_script} "
            f"--text \"{args.text}\" "
            f"--speaker_wav \"{args.speaker_wav}\" "
            f"--model_dir \"{args.model_dir}\" "
            f"--output_dir \"{args.output_dir}\" "
        )
        
        run_command(cmd, "Running TTS Inference")
        
        logger.info(f"Done! Check output in {args.output_dir}")
        
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
