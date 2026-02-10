import os
import sys
import subprocess
import logging
import datetime
import traceback
import shutil
import torch

# Kaggle base directories
BASE_DIR = "/kaggle/working/snsw"
DATA_BASE = "/kaggle/working/data"
LOG_DIR = os.path.join(BASE_DIR, "dev")

def setup_logging():
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
 # Line 27付近の依存関係インストール部分
        run_command("pip install --no-cache-dir transformers==4.35.2 datasets peft safetensors librosa yt-dlp", 
                "Installing base libraries")

# faster-whisperを別途インストール
        run_command("pip install --no-cache-dir faster-whisper", "Installing faster-whisper")

# Coqui TTSのインストール - より堅牢に
        try:
            run_command("pip install --no-cache-dir TTS", "Installing TTS")
        except Exception as e:
            logger.warning(f"Standard 'TTS' install failed: {e}. Trying from source.")
            run_command("pip install --no-cache-dir git+https://github.com/coqui-ai/TTS.git@dev", 
                        "Installing TTS from source")
    
    return logging.getLogger(__name__)




logger = setup_logging()

def run_command(cmd, description, cwd=None):
    logger.info(f"Starting: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
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
        logger.info("=== SNSW Kaggle One-Click Training Pipeline (Robust Edition) Started ===")
        
        # 1. Install dependencies
        run_command("pip install --no-cache-dir transformers==4.35.2 datasets peft safetensors librosa yt-dlp faster-whisper", "Installing base libraries")
        try:
            run_command("pip install --no-cache-dir coqui-tts", "Installing coqui-tts")
        except Exception as e:
            logger.warning(f"Standard 'coqui-tts' install failed: {e}. Trying to install from source.")
            run_command("pip install --no-cache-dir git+https://github.com/coqui-ai/TTS.git", "Installing TTS from source")
        
        # 2. Prepare directories
        RAW_DIR = os.path.join(DATA_BASE, "raw")
        WAV_DIR = os.path.join(DATA_BASE, "wav")
        os.makedirs(RAW_DIR, exist_ok=True)
        os.makedirs(WAV_DIR, exist_ok=True)
        
        # 3. Download source from YouTube
        YOUTUBE_URL = "https://www.youtube.com/watch?v=pw5nR3ym8XA"
        run_command(f'yt-dlp -x --audio-format wav --audio-quality 0 -o "{RAW_DIR}/input.%(ext)s" {YOUTUBE_URL}', "Downloading Audio")
        
        # 4. Preprocess Audio
        run_command(f"ffmpeg -i {RAW_DIR}/input.wav -ar 22050 -ac 1 {WAV_DIR}/processed.wav -y", "Converting Audio")
        run_command(f"ffmpeg -i {WAV_DIR}/processed.wav -ss 0 -t 60 {WAV_DIR}/sample.wav -y", "Creating 60s sample")
        
        # 5. Auto-transcription with faster-whisper
        metadata_path = os.path.join(DATA_BASE, "metadata.csv")
        try:
            from faster_whisper import WhisperModel
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            
            logger.info(f"Loading Whisper model (device={device}, compute_type={compute_type})...")
            model = WhisperModel("base", device=device, compute_type=compute_type)
            segments, _ = model.transcribe(os.path.join(WAV_DIR, "sample.wav"), language="ja")
            transcript = "".join(segment.text for segment in segments).strip()
            
            with open(metadata_path, "w") as f:
                f.write(f"sample.wav|{transcript}|shinsho\n")
            logger.info(f"Transcription completed: {transcript[:50]}...")
        except Exception as e:
            logger.warning(f"Whisper transcription failed, falling back to default text. Error: {e}")
            with open(metadata_path, "w") as f:
                f.write("sample.wav|えー、お馴染みの一席でございます。志ん生でございます。|shinsho\n")

        # 6. Run LoRA Training
        train_script = os.path.join(BASE_DIR, "src/lora/train_xtts.py")
        if not os.path.exists(train_script):
            train_script = os.path.abspath("src/lora/train_xtts.py")
            
        run_command(f"python {train_script} --dataset_path {metadata_path} --epochs 1", "Running LoRA Training")
        
        logger.info("=== Pipeline Completed Successfully! ===")
    except Exception as e:
        logger.error("!!! Pipeline Failed !!!")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
