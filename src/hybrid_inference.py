import os
import sys
import argparse
import time
from pathlib import Path
import torch

# Add src to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.append(str(PROJECT_ROOT / "src"))

try:
    from TTS.api import TTS
    from tools.rvc_engine import RVCEngine
except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure you have installed the required dependencies.")

def run_hybrid_inference(text, speaker_wav, xtts_model_path, rvc_model_path, output_path, device=None):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 1. XTTS-v2 Inference
    print(f"--- Step 1: XTTS-v2 Generation ---")
    print(f"Text: {text}")
    temp_xtts_path = "temp_xtts_output.wav"
    
    try:
        # Initialize XTTS
        tts = TTS(model_path=xtts_model_path if xtts_model_path else "tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
        # Generate audio
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language="ja",
            file_path=temp_xtts_path
        )
        print(f"XTTS-v2 generation completed: {temp_xtts_path}")
        
    except Exception as e:
        print(f"XTTS-v2 Error: {e}")
        return None

    # 2. RVC Voice Conversion
    print(f"\n--- Step 2: RVC Voice Conversion ---")
    if not rvc_model_path or not os.path.exists(rvc_model_path):
        print("RVC model path not provided or not found. Skipping RVC step.")
        os.rename(temp_xtts_path, output_path)
        print(f"Final output saved to: {output_path} (XTTS only)")
        return output_path

    try:
        rvc = RVCEngine(rvc_model_path, device=device)
        rvc.convert(temp_xtts_path, output_path)
        print(f"RVC conversion completed: {output_path}")
        
        # Cleanup temp file
        if os.path.exists(temp_xtts_path):
            os.remove(temp_xtts_path)
            
    except Exception as e:
        print(f"RVC Error: {e}")
        print("Falling back to XTTS-v2 output.")
        os.rename(temp_xtts_path, output_path)
        
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SNSW Hybrid Inference (XTTS-v2 + RVC)")
    parser.add_argument("--text", type=str, required=True, help="Text to synthesize")
    parser.add_argument("--speaker_wav", type=str, required=True, help="Reference speaker wav for XTTS")
    parser.add_argument("--xtts_model", type=str, default=None, help="Path to XTTS model checkpoint")
    parser.add_argument("--rvc_model", type=str, default=None, help="Path to RVC model (.pth)")
    parser.add_argument("--output", type=str, default="tts_outputs/hybrid_output.wav", help="Output path")
    
    args = parser.parse_args()
    
    run_hybrid_inference(
        text=args.text,
        speaker_wav=args.speaker_wav,
        xtts_model_path=args.xtts_model,
        rvc_model_path=args.rvc_model,
        output_path=args.output
    )
