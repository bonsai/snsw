#!/usr/bin/env python
"""
StyleTTS2 を使用したTTS実行スクリプト
高速・高品質な音声合成
"""
import os
import sys
import json
from datetime import datetime

def process_tts_styletts2(text, speaker_wav, output_file):
    print(f"\n--- StyleTTS2 生成開始 ---")
    print(f"テキスト: {text}")
    print(f"参照音声: {speaker_wav}")
    print(f"出力先: {output_file}")
    
    try:
        import torch
        import torchaudio
        from styletts2 import tts
        import yaml
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用デバイス: {device}")
        
        model_dir = "/app/models/styletts2"
        
        if not os.path.exists(model_dir):
            print(f"エラー: モデルディレクトリ {model_dir} が見つかりません")
            return False
        
        # モデルディレクトリ
        models_path = os.path.join(model_dir, "Models")
        
        if not os.path.exists(models_path):
            print(f"エラー: Models ディレクトリ {models_path} が見つかりません")
            return False
        
        # TTS初期化
        model = tts.StyleTTS2(models_path=models_path, device=device)
        
        # 音声生成
        audio = model.inference(text=text, speaker_wav=speaker_wav, language="ja")
        
        # WAVファイルに保存
        import soundfile as sf
        sf.write(output_file, audio, 22050)  # 22.05kHz
        
        print(f"完了: {output_file}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    TEXT_JSON_PATH = "SOURCE/text.json"
    if not os.path.exists(TEXT_JSON_PATH):
        TEXT_JSON_PATH = "src/text.json"
    
    DEFAULT_SPEAKER_WAV = "SOURCE/001.wav"
    OUTPUT_DIR = "tts_outputs"
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    if os.path.exists(TEXT_JSON_PATH):
        print(f"JSONファイルを読み込み中: {TEXT_JSON_PATH}")
        with open(TEXT_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        for entry in data:
            entry_id = entry.get("id", "unknown")
            text = entry.get("text", "")
            if not text:
                continue
            
            output_file = os.path.join(OUTPUT_DIR, f"styletts2-audio-{entry_id}-{timestamp}.wav")
            process_tts_styletts2(text, DEFAULT_SPEAKER_WAV, output_file)
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        text = sys.argv[1] if len(sys.argv) > 1 else "こんにちは。StyleTTS2 のテストです。"
        speaker_wav = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SPEAKER_WAV
        output_file = sys.argv[3] if len(sys.argv) > 3 else os.path.join(OUTPUT_DIR, f"styletts2-audio-{timestamp}.wav")
        process_tts_styletts2(text, speaker_wav, output_file)

if __name__ == "__main__":
    main()
