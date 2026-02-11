#!/usr/bin/env python
import os
import sys
import json
import torch
from datetime import datetime

# Fish-Speech のパス設定（Docker内マウント先）
FISH_SPEECH_PATH = "/app/models/fish-speech"

def process_fish_speech(text, speaker_wav, output_file):
    print(f"\n--- Fish-Speech 生成開始 ---")
    print(f"テキスト: {text}")
    print(f"参照音声: {speaker_wav}")
    print(f"出力先: {output_file}")
    
    try:
        # from fish_speech.inference import generate_audio
        print("Fish-Speech モデルをロード中...")
        # generate_audio(text, speaker_wav, output_file, model_path=FISH_SPEECH_PATH)
        print("生成完了（ダミー出力）")
    except ImportError:
        print("Error: fish-speech のライブラリが見つかりません。")

def main():
    TEXT_JSON_PATH = "SOURCE/text.json"
    if not os.path.exists(TEXT_JSON_PATH):
        TEXT_JSON_PATH = "src/text.json"
    
    DEFAULT_SPEAKER_WAV = "SOURCE/001.wav"
    OUTPUT_DIR = "tts_outputs"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if os.path.exists(TEXT_JSON_PATH):
        with open(TEXT_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        for entry in data:
            entry_id = entry.get("id", "unknown")
            text = entry.get("text", "")
            if not text: continue
            output_file = os.path.join(OUTPUT_DIR, f"fish-speech-audio-{entry_id}-{timestamp}.wav")
            process_fish_speech(text, DEFAULT_SPEAKER_WAV, output_file)
    else:
        text = sys.argv[1] if len(sys.argv) > 1 else "こんにちは、Fish-Speechのテストです。"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = os.path.join(OUTPUT_DIR, f"fish-speech-audio-single-{timestamp}.wav")
        process_fish_speech(text, DEFAULT_SPEAKER_WAV, output_file)

if __name__ == "__main__":
    main()
