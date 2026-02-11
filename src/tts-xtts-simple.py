#!/usr/bin/env python
"""シンプルなTTS実行スクリプト（モデル自動ダウンロード）"""
import os
import sys
from TTS.api import TTS

def main():
    # コマンドライン引数からテキストを取得
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = "こんにちは。これはテストです。"
    
    # 参照音声（speaker_wav）
    if len(sys.argv) > 2:
        speaker_wav = sys.argv[2]
    else:
        speaker_wav = "/app/ARCHIVE/v3/INADA_audio.wav"
    
    # 出力ファイル名
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    else:
        output_file = "/app/tts_outputs/xtts-audio-simple.wav"
    
    print(f"テキスト: {text}")
    print(f"参照音声: {speaker_wav}")
    print(f"出力先: {output_file}")
    print("\nモデルをロード中...")
    
    # XTTSモデルを初期化（初回実行時は自動でダウンロード）
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
    
    print("音声を生成中...")
    
    # 音声生成
    tts.tts_to_file(
        text=text,
        speaker_wav=speaker_wav,
        language="ja",
        file_path=output_file
    )
    
    print(f"\n完了！ {output_file} に保存しました。")

if __name__ == "__main__":
    main()
