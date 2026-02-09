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
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"Successfully completed: {description}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error in {description}:")
        logger.error(f"Exit Code: {e.returncode}")
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise

def main():
    try:
        logger.info("=== SNSW Kaggle One-Click Training Pipeline (Auto-Transcription) Started ===")
        
        logger.info("Installing dependencies...")
        run_command("pip install --no-cache-dir transformers==4.35.2 datasets peft safetensors librosa yt-dlp faster-whisper", "Installing base libraries")
        
        try:
            run_command("pip install --no-cache-dir coqui-tts", "Installing coqui-tts")
        except:
            logger.warning("Standard TTS install failed, trying alternative...")
            run_command("pip install --no-cache-dir git+https://github.com/coqui-ai/TTS.git", "Installing TTS from source")
        
        YOUTUBE_URL = "https://www.youtube.com/watch?v=pw5nR3ym8XA"
        RAW_DIR = "/kaggle/working/data/raw"
        WAV_DIR = "/kaggle/working/data/wav"
        os.makedirs(RAW_DIR, exist_ok=True)
        os.makedirs(WAV_DIR, exist_ok=True)
        
        logger.info(f"Downloading audio from YouTube: {YOUTUBE_URL}")
        run_command(f'yt-dlp -x --audio-format wav --audio-quality 0 -o "{RAW_DIR}/input.%(ext)s" {YOUTUBE_URL}', "Downloading YouTube Audio")
        
        run_command(f"ffmpeg -i {RAW_DIR}/input.wav -ar 22050 -ac 1 {WAV_DIR}/processed.wav -y", "Converting Audio")
        run_command(f"ffmpeg -i {WAV_DIR}/processed.wav -ss 0 -t 60 {WAV_DIR}/sample.wav -y", "Creating 60s sample")
        
        logger.info("Starting automatic transcription with faster-whisper...")
        try:
            from faster_whisper import WhisperModel
            model_size = "base"
            device = "cuda" if subprocess.run("nvidia-smi", shell=True).returncode == 0 else "cpu"
            logger.info(f"Loading Whisper model '{model_size}' on {device}...")
            
            whisper_model = WhisperModel(model_size, device=device, compute_type="float16" if device == "cuda" else "int8")
            segments, _ = whisper_model.transcribe(f"{WAV_DIR}/sample.wav", language="ja")
            transcript = "".join(segment.text for segment in segments).strip()
            
            logger.info(f"Transcription completed: {transcript[:100]}...")
            
            metadata_path = "/kaggle/working/data/metadata.csv"
            with open(metadata_path, "w") as f:
                f.write(f"sample.wav|{transcript}|shinsho\n")
            
        except Exception as e:
            logger.error("Transcription failed, falling back to dummy metadata.")
            metadata_path = "/kaggle/working/data/metadata.csv"
            with open(metadata_path, "w") as f:
                f.write("sample.wav|えー、お馴染みの一席でございます。志ん生でございます。|shinsho\n")

        logger.info("Starting LoRA training...")
        run_command(f"python train_xtts_lora.py --dataset_path {metadata_path} --epochs 1", "Running LoRA Training")
        
        logger.info("=== Pipeline Completed Successfully! ===")
    except Exception as e:
        logger.error("!!! Pipeline Failed !!!")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
