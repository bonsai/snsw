#!/usr/bin/env python
"""
複数モデル対応TTS実行スクリプト
以下の5つのモデルから選択して実行可能です。
コメントアウトを切り替えて使用してください。
"""
import os
import sys
import torch
import librosa
import soundfile as sf
import json
from datetime import datetime

def process_tts(model_type, text, speaker_wav, output_file):
    print(f"\n--- 生成開始 ---")
    print(f"モデル: {model_type}")
    print(f"テキスト: {text}")
    print(f"参照音声: {speaker_wav}")
    print(f"出力先: {output_file}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用デバイス: {device}")

    if model_type == "xtts":
        from TTS.api import TTS
        # Docker内では /app/models/TTS/xtts_v2 などのパスを想定
        # 無ければ自動ダウンロード
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        tts.tts_to_file(text=text, speaker_wav=speaker_wav, language="ja", file_path=output_file)

    elif model_type == "qwen2-audio":
        from transformers import Qwen2AudioForConditionalGeneration, AutoProcessor
        model_name = "Qwen/Qwen2-Audio-7B-Instruct"
        processor = AutoProcessor.from_pretrained(model_name)
        model = Qwen2AudioForConditionalGeneration.from_pretrained(model_name, device_map="cpu")
        print("Qwen2-Audio での生成（デモ）")

    elif model_type == "gpt-sovits":
        print("GPT-SoVITS での生成")
        model_path = "C:/models/gpt-sovits"
        # 実際のロード処理（例）
        # from gpt_sovits.inference import TTS
        # tts = TTS(model_path=model_path)

    elif model_type == "fish-speech":
        print("Fish-Speech での生成")
        model_path = "C:/models/fish-speech"
        # from fish_speech.inference import generate_audio
        # generate_audio(text, speaker_wav, output_file, model_path=model_path)

    elif model_type == "styletts2":
        print("StyleTTS2 での生成")
        model_path = "C:/models/styletts2"
        # import styletts2
        # model = styletts2.load_model(os.path.join(model_path, "config.yml"))
        # model.synthesize(text, output_file)

    print(f"完了: {output_file}")

def main():
    # --- 設定項目 ---
    # 1. XTTS v2 (Coqui TTS) - 高品質・多言語
    MODEL_TYPE = "xtts"
    
    # 2. Qwen2-Audio (qwntts) - 音声理解・生成（巨大モデル）
    # MODEL_TYPE = "qwen2-audio"
    
    # 3. GPT-SoVITS - 少量のデータで強力なクローン（日本語に強い）
    # MODEL_TYPE = "gpt-sovits"
    
    # 4. Fish-Speech - SOTAな音声生成（最新モデル）
    # MODEL_TYPE = "fish-speech"
    
    # 5. StyleTTS2 - 高速・高品質な音声合成
    # MODEL_TYPE = "styletts2"
    
    # --- パス設定 ---
    # text.json が SOURCE ディレクトリにある場合を優先する
    TEXT_JSON_PATH = "SOURCE/text.json"
    if not os.path.exists(TEXT_JSON_PATH):
        TEXT_JSON_PATH = "src/text.json"
        print(f"SOURCE/text.json が見つからないため {TEXT_JSON_PATH} を使用します")
    
    # Docker内でのマウントパスを考慮
    DEFAULT_SPEAKER_WAV = "SOURCE/001.wav"
    if not os.path.exists(DEFAULT_SPEAKER_WAV):
        # 存在しない場合は、適当なwavファイルを探索
        import glob
        wav_files = glob.glob("SOURCE/*.wav")
        if wav_files:
            DEFAULT_SPEAKER_WAV = wav_files[0]
            print(f"参照音声が見つからないため {DEFAULT_SPEAKER_WAV} を使用します")
    
    OUTPUT_DIR = "tts_outputs"

    # 出力ディレクトリの作成
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"ディレクトリを作成しました: {OUTPUT_DIR}")

    # text.json が存在するか確認
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
            
            # 命名規則: (モデル-)役割-特徴-タイムスタンプ.拡張子
            # text.json 用に ID を特徴部分に含める
            output_file = os.path.join(OUTPUT_DIR, f"{MODEL_TYPE}-audio-{entry_id}-{timestamp}.wav")
            process_tts(MODEL_TYPE, text, DEFAULT_SPEAKER_WAV, output_file)
    else:
        # 引数から単発処理
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        text = sys.argv[1] if len(sys.argv) > 1 else "こんにちは。モデル切り替えのテストです。"
        speaker_wav = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SPEAKER_WAV
        output_file = sys.argv[3] if len(sys.argv) > 3 else os.path.join(OUTPUT_DIR, f"{MODEL_TYPE}-audio-multi-{timestamp}.wav")
        process_tts(MODEL_TYPE, text, speaker_wav, output_file)

    print(f"\nすべての処理が完了しました。")

if __name__ == "__main__":
    main()
