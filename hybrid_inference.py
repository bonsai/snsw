import os
import torch
import argparse
from TTS.api import TTS
from peft import PeftModel, LoraConfig, get_peft_model

def load_xtts_with_lora(model_path, lora_path=None):
    """XTTS-v2モデルをロードし、LoRA重みを適用する"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS(model_path).to(device)
    
    if lora_path and os.path.exists(lora_path):
        print(f"Loading LoRA weights from {lora_path}...")
        # XTTSのGPT部分にLoRAを適用
        xtts_gpt = tts.model.gpt
        tts.model.gpt = PeftModel.from_pretrained(xtts_gpt, lora_path)
    
    return tts

def run_rvc(input_wav, output_wav, rvc_model_path, f0_up_key=0):
    """RVCを使用して音声変換を行う（外部CLI呼び出しの例）"""
    # 実際にはRVCのディレクトリパスや推論スクリプトのパスを指定してください
    rvc_script = "path/to/rvc/infer_cli.py" 
    
    if not os.path.exists(rvc_script):
        print(f"Warning: RVC script not found at {rvc_script}. Skipping RVC step.")
        return input_wav

    cmd_list = ["python", rvc_script, "--model", rvc_model_path, "--input", input_wav, "--output", output_wav, "--f0_up_key", str(f0_up_key)]
    print(f"Running RVC: {' '.join(cmd_list)}")
    subprocess.run(cmd_list, check=True)
    return output_wav

def main():
    parser = argparse.ArgumentParser(description="XTTS-v2 + RVC Hybrid Inference")
    parser.add_argument("--text", type=str, required=True, help="Text to synthesize")
    parser.add_argument("--speaker_wav", type=str, required=True, help="Reference speaker wav")
    parser.add_argument("--lora_path", type=str, default=None, help="Path to XTTS LoRA weights")
    parser.add_argument("--rvc_model", type=str, default=None, help="Path to RVC .pth model")
    parser.add_argument("--output", type=str, default="output_final.wav", help="Final output path")
    
    args = parser.parse_args()

    # 1. XTTS-v2で音声生成
    tts = load_xtts_with_lora("tts_models/multilingual/multi-dataset/xtts_v2", args.lora_path)
    temp_xtts_out = "temp_xtts.wav"
    
    tts.tts_to_file(
        text=args.text,
        speaker_wav=args.speaker_wav,
        language="ja",
        file_path=temp_xtts_out
    )
    print(f"XTTS generation completed: {temp_xtts_out}")

    # 2. RVCで質感変換
    if args.rvc_model:
        run_rvc(temp_xtts_out, args.output, args.rvc_model)
        print(f"Hybrid synthesis completed: {args.output}")
    else:
        os.rename(temp_xtts_out, args.output)
        print(f"Synthesis completed (XTTS only): {args.output}")

if __name__ == "__main__":
    main()
