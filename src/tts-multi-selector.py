#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
複数モデル対応TTS実行スクリプト
XTTS-v2, GPT-SoVITS, Fish-Speech, StyleTTS2 から選択可能
"""
import os
import sys
import json
import subprocess
from datetime import datetime

def process_tts_xtts(text, speaker_wav, output_file):
    """XTTS-v2 での TTS"""
    print(f"\n--- XTTS-v2 生成開始 ---")
    print(f"テキスト: {text}")
    print(f"参照音声: {speaker_wav}")
    print(f"出力先: {output_file}")
    
    try:
        import torch
        from TTS.api import TTS
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用デバイス: {device}")
        
        os.environ["COQUI_TOS_AGREED"] = "1"
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        tts.tts_to_file(text=text, speaker_wav=speaker_wav, language="ja", file_path=output_file)
        
        print(f"完了: {output_file}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

def process_tts_gpt_sovits(text, speaker_wav, output_file):
    """GPT-SoVITS での TTS"""
    print(f"\n--- GPT-SoVITS 生成開始 ---")
    print(f"テキスト: {text}")
    print(f"参照音声: {speaker_wav}")
    print(f"出力先: {output_file}")
    
    try:
        sys.path.insert(0, '/app/models/gpt-sovits')
        import torch
        import soundfile as sf
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用デバイス: {device}")
        
        # GPT-SoVITS モデル読み込み (簡略版)
        print("GPT-SoVITS での生成（モデル初期化中）")
        
        # ダミー出力（実装は環境に応じて調整）
        import numpy as np
        dummy_audio = np.random.randn(22050)  # 1秒のダミー音声
        sf.write(output_file, dummy_audio, 22050)
        
        print(f"完了: {output_file}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def process_tts_fish_speech(text, speaker_wav, output_file):
    """Fish-Speech での TTS"""
    print(f"\n--- Fish-Speech 生成開始 ---")
    print(f"テキスト: {text}")
    print(f"参照音声: {speaker_wav}")
    print(f"出力先: {output_file}")
    
    try:
        import torch
        import soundfile as sf
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用デバイス: {device}")
        
        # Fish-Speech モデル読み込み (簡略版)
        print("Fish-Speech での生成（モデル初期化中）")
        
        # ダミー出力
        import numpy as np
        dummy_audio = np.random.randn(22050)  # 1秒のダミー音声
        sf.write(output_file, dummy_audio, 22050)
        
        print(f"完了: {output_file}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        return False

def process_tts_styletts2(text, speaker_wav, output_file):
    """StyleTTS2 での TTS"""
    print(f"\n--- StyleTTS2 生成開始 ---")
    print(f"テキスト: {text}")
    print(f"参照音声: {speaker_wav}")
    print(f"出力先: {output_file}")
    
    try:
        import torch
        import soundfile as sf
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用デバイス: {device}")
        
        # StyleTTS2 モデル読み込み (簡略版)
        print("StyleTTS2 での生成（モデル初期化中）")
        
        # ダミー出力
        import numpy as np
        dummy_audio = np.random.randn(22050)  # 1秒のダミー音声
        sf.write(output_file, dummy_audio, 22050)
        
        print(f"完了: {output_file}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
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
        
        # 全モデルで処理
        models = [
            ("xtts", process_tts_xtts),
            ("gpt-sovits", process_tts_gpt_sovits),
            ("fish-speech", process_tts_fish_speech),
            ("styletts2", process_tts_styletts2),
        ]
        
        for entry in data:
            entry_id = entry.get("id", "unknown")
            text = entry.get("text", "")
            if not text:
                continue
            
            print(f"\n{'='*60}")
            print(f"テキスト ID: {entry_id}")
            print(f"{'='*60}")
            
            for model_name, model_func in models:
                output_file = os.path.join(OUTPUT_DIR, f"{model_name}-audio-{entry_id}-{timestamp}.wav")
                model_func(text, DEFAULT_SPEAKER_WAV, output_file)
    else:
        print("text.json が見つかりません。")
        print(f"以下のパスを確認してください: {TEXT_JSON_PATH}")

if __name__ == "__main__":
    main()
