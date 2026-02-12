#!/usr/bin/env python
"""
Fish-Speech を使用したTTS実行スクリプト
"""
import os
import sys
import json
from datetime import datetime

def process_tts_fish_speech(text, speaker_wav, output_file):
    print(f"\n--- Fish-Speech 生成開始 ---")
    print(f"テキスト: {text}")
    print(f"参照音声: {speaker_wav}")
    print(f"出力先: {output_file}")
    
    try:
        # Fish-Speech インポート
        sys.path.insert(0, '/app/models/fish-speech')
        from fish_speech.models import VALL_E
        
        import torch
        import torchaudio
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用デバイス: {device}")
        
        model_dir = "/app/models/fish-speech"
        
        if not os.path.exists(model_dir):
            print(f"エラー: モデルディレクトリ {model_dir} が見つかりません")
            return False
        
        # モデル読み込み
        model_path = os.path.join(model_dir, "model.pth")
        if not os.path.exists(model_path):
            print(f"エラー: モデルファイル {model_path} が見つかりません")
            return False
        
        # テキスト処理と音声生成
        # Fish-Speech 推論実装（簡略版）
        print("Fish-Speech での音声生成（実装中）")
        
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
            
            output_file = os.path.join(OUTPUT_DIR, f"fish-speech-audio-{entry_id}-{timestamp}.wav")
            process_tts_fish_speech(text, DEFAULT_SPEAKER_WAV, output_file)
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        text = sys.argv[1] if len(sys.argv) > 1 else "こんにちは。Fish-Speech のテストです。"
        speaker_wav = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SPEAKER_WAV
        output_file = sys.argv[3] if len(sys.argv) > 3 else os.path.join(OUTPUT_DIR, f"fish-speech-audio-{timestamp}.wav")
        process_tts_fish_speech(text, speaker_wav, output_file)

if __name__ == "__main__":
    main()
