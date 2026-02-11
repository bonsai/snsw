#!/usr/bin/env python
import os
import sys
import json
import torch
from datetime import datetime

# GPT-SoVITS のパス設定（Docker内マウント先）
GPT_SOVITS_PATH = "/app/models/gpt-sovits"

def process_gpt_sovits(text, speaker_wav, output_file):
    print(f"\n--- GPT-SoVITS 生成開始 ---")
    print(f"テキスト: {text}")
    print(f"参照音声: {speaker_wav}")
    print(f"出力先: {output_file}")
    
    # 実際のロード処理（環境に応じて適宜修正が必要）
    try:
        # GPT-SoVITSのリポジトリがPYTHONPATHに含まれている想定
        # from GPT_SoVITS.inference_webui import get_tts_wav
        print("GPT-SoVITS モデルをロード中...")
        # 実装例:
        # wav = get_tts_wav(text, speaker_wav, ...)
        # sf.write(output_file, wav, 32000)
        print("生成完了（ダミー出力: 実際のライブラリ構成に合わせて実装を調整してください）")
    except ImportError:
        print("Error: GPT-SoVITS のライブラリが見つかりません。")

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
            output_file = os.path.join(OUTPUT_DIR, f"gpt-sovits-audio-{entry_id}-{timestamp}.wav")
            process_gpt_sovits(text, DEFAULT_SPEAKER_WAV, output_file)
    else:
        text = sys.argv[1] if len(sys.argv) > 1 else "こんにちは、GPT-SoVITSのテストです。"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = os.path.join(OUTPUT_DIR, f"gpt-sovits-audio-single-{timestamp}.wav")
        process_gpt_sovits(text, DEFAULT_SPEAKER_WAV, output_file)

if __name__ == "__main__":
    main()
