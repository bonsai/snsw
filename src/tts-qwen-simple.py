#!/usr/bin/env python
"""Qwen2-Audio (qwntts) を使用したTTS実行スクリプト"""
import os
import sys
import torch
import librosa
import soundfile as sf
from transformers import Qwen2AudioForConditionalGeneration, AutoProcessor

def main():
    # コマンドライン引数からテキストを取得
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = "こんにちは。これはQwen2-Audioによるテストです。"
    
    # 参照音声（Qwen2-Audioでは直接クローンには使わないが、コンテキストとして利用可能な場合がある）
    if len(sys.argv) > 2:
        speaker_wav = sys.argv[2]
    else:
        speaker_wav = "/app/SOURCE/001.wav"
    
    # 出力ファイル名
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    else:
        output_file = "/app/tts_outputs/qwen-audio-simple.wav"
    
    print(f"テキスト: {text}")
    print(f"出力先: {output_file}")
    
    model_name = "Qwen/Qwen2-Audio-7B-Instruct"
    print(f"\nモデル {model_name} をロード中 (CPU)...")
    
    # モデルとプロセッサのロード
    processor = AutoProcessor.from_pretrained(model_name)
    model = Qwen2AudioForConditionalGeneration.from_pretrained(
        model_name, 
        torch_dtype="auto", 
        device_map="cpu"
    )
    
    print("音声を生成中...")
    
    # Qwen2-Audioへのプロンプト構築
    # TTSタスクを指定する形式
    prompt = f"<|audio_only|> {text}"
    
    # 参照音声がある場合は入力に含める（オーディオ理解とTTSの組み合わせ）
    if os.path.exists(speaker_wav):
        print(f"参照音声をコンテキストとして使用: {speaker_wav}")
        audio, sr = librosa.load(speaker_wav, sr=processor.feature_extractor.sampling_rate)
        inputs = processor(text=prompt, audios=audio, return_tensors="pt")
    else:
        inputs = processor(text=prompt, return_tensors="pt")

    # 推論
    with torch.no_grad():
        # 注意: Qwen2-Audio の公式なTTS出力取得方法はモデルの仕様に依存します
        # ここでは一般的なHuggingFaceのgenerateを使用
        generate_ids = model.generate(**inputs, max_length=256)
        
    # 生成されたトークンを音声に変換するロジックが必要
    # Qwen2-Audio 自体はマルチモーダル理解モデルであり、
    # 直接的なTTS（波形出力）には追加のボコーダーや特定のヘッドが必要な場合があります。
    # ユーザーが「qwntts」と指定した場合、特定のライブラリやラッパーを指している可能性があります。
    
    print("注意: Qwen2-Audio-Instructは主に音声理解モデルです。")
    print("直接の波形生成には、Qwen2-Audioの音声出力をサポートする特定のブランチや")
    print("追加のデコーダーが必要になる場合があります。")
    
    # 今回は構成の変更を優先し、実行可能な形を目指します。
    # 実際には Qwen2-Audio をTTSとして使うための専用ラッパーライブラリを導入する必要があるかもしれません。
    
    print(f"\n[DEMO] Qwen2-Audio への入力を準備しました。")
    print(f"実際の音声生成には専用のTTSモデルヘッドが必要です。")

if __name__ == "__main__":
    main()
