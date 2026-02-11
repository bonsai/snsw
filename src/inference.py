import os
import sys
import torch
import torchaudio
import argparse
from pathlib import Path
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

def load_model(checkpoint_dir):
    """
    XTTSモデルをロードする
    checkpoint_dir: config.json, model.pth, vocab.json 等があるディレクトリ
    """
    print(f"Loading model from {checkpoint_dir}...")
    
    # Configのロード
    config_path = os.path.join(checkpoint_dir, "config.json")
    if not os.path.exists(config_path):
        # original_xtts_config.jsonを探す（LoRA学習後の構成など）
        config_path = os.path.join(checkpoint_dir, "original_xtts_config.json")
        
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found in {checkpoint_dir}")

    config = XttsConfig()
    config.load_json(config_path)
    
    # モデルの初期化
    model = Xtts.init_from_config(config)
    
    # 重みのロード
    # 通常のXTTSモデル構造を想定
    model.load_checkpoint(config, checkpoint_dir=checkpoint_dir, eval=True)
    
    if torch.cuda.is_available():
        model.cuda()
    
    print("Model loaded successfully!")
    return model

def run_inference(model, text, speaker_wav, language="ja", output_path="output.wav"):
    """
    音声合成を実行する
    """
    print(f"Generating audio for text: '{text[:20]}...'")
    print(f"Speaker reference: {speaker_wav}")
    
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
        audio_path=[speaker_wav]
    )
    
    out = model.inference(
        text,
        language,
        gpt_cond_latent,
        speaker_embedding,
        temperature=0.7, # パラメータは調整可能にする
    )
    
    # 保存
    torchaudio.save(output_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
    print(f"Saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="XTTS Inference Script")
    parser.add_argument("--text", type=str, required=True, help="Text to synthesize")
    parser.add_argument("--speaker_wav", type=str, required=True, help="Path to reference speaker wav file")
    parser.add_argument("--language", type=str, default="ja", help="Language code (ja, en, etc.)")
    parser.add_argument("--model_dir", type=str, required=True, help="Directory containing model checkpoints")
    parser.add_argument("--output_dir", type=str, default="output", help="Output directory")
    parser.add_argument("--output_filename", type=str, default="generated.wav", help="Output filename")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    output_path = os.path.join(args.output_dir, args.output_filename)
    
    model = load_model(args.model_dir)
    run_inference(model, args.text, args.speaker_wav, args.language, output_path)

if __name__ == "__main__":
    main()
