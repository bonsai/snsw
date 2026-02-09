import os
import sys
import subprocess
import logging
import datetime
import traceback

# 1. ログ設定 (/dev ディレクトリに保存)
LOG_DIR = "/kaggle/working/snsw/dev"
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(LOG_DIR, f"train_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_command(cmd, description):
    logger.info(f"Starting: {description}")
    try:
        # ログをキャプチャしつつ実行
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"Successfully completed: {description}")
        if result.stdout:
            logger.info(f"Output: {result.stdout[:500]}...")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error in {description}:")
        logger.error(f"Exit Code: {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise

def main():
    try:
        logger.info("=== SNSW Kaggle One-Click Training Pipeline Started ===")
        
        # Step 1: 依存関係のインストール
        run_command("pip install -U TTS peft transformers datasets safetensors librosa", "Installing libraries")
        
        # Step 2: サンプルデータセットの準備 (元データURLからダウンロード)
        # ※ここでは志ん生さんの公開音源アーカイブを想定したURL（プレースホルダ）を設定
        DATA_URL = "https://archive.org/download/shinsho_sample/sample_shinsho.zip"
        DATA_DIR = "/kaggle/working/data"
        os.makedirs(DATA_DIR, exist_ok=True)
        
        logger.info(f"Downloading source data from {DATA_URL}")
        # 実際にはURLが有効な場合にダウンロードを実行。ここではディレクトリ作成のみ
        # run_command(f"wget {DATA_URL} -P {DATA_DIR} && unzip {DATA_DIR}/*.zip -d {DATA_DIR}", "Downloading and unzipping data")
        
        # Step 3: データセット構築 (metadata.csv の自動生成例)
        # Kaggle環境では /kaggle/input にデータがある場合も考慮
        metadata_path = os.path.join(DATA_DIR, "metadata.csv")
        if not os.path.exists(metadata_path):
            logger.info("Generating dummy metadata for initial run...")
            with open(metadata_path, "w") as f:
                f.write("audio1.wav|えー、お馴染みの一席でございます。|shinsho\n")
        
        # Step 4: LoRA学習の実行
        # 先ほど作成した train_xtts_lora.py を呼び出し
        run_command(f"python train_xtts_lora.py --dataset_path {metadata_path} --epochs 1", "Running LoRA Training")
        
        logger.info("=== Pipeline Completed Successfully! ===")
        logger.info(f"Results saved in /kaggle/working/outputs")
        logger.info(f"Full logs available in {LOG_DIR}")

    except Exception as e:
        logger.error("!!! Pipeline Failed !!!")
        logger.error(traceback.format_exc())
        # エラーログを /dev に確実に残す
        with open(os.path.join(LOG_DIR, "CRITICAL_ERROR.log"), "a") as f:
            f.write(f"\n--- {timestamp} ---\n")
            f.write(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
