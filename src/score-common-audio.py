#!/usr/bin/env python
import os
import librosa
import numpy as np
import torch
import json
from pathlib import Path

def calculate_physical_stats(y):
    """物理的な統計情報を算出"""
    return {
        "mean_amplitude": float(np.mean(np.abs(y))),
        "max_amplitude": float(np.max(np.abs(y))),
        "rms": float(np.sqrt(np.mean(y**2)))
    }

def predict_mos(y, sr):
    """
    MOS (自然さ) を予測するプレースホルダ
    実際には NISQA などのモデルをロードして計算する
    """
    # デモ用にランダムな値を返す (3.0 - 4.8)
    return float(np.random.uniform(3.0, 4.8))

def calculate_similarity(y, ref_y):
    """
    話者類似度を算出するプレースホルダ
    実際には Resemblyzer 等の埋め込みベクトルで計算する
    """
    # デモ用にランダムな値を返す (0.7 - 0.98)
    return float(np.random.uniform(0.7, 0.98))

def score_audio(audio_path, ref_path=None):
    print(f"\n--- 採点中: {os.path.basename(audio_path)} ---")
    
    y, sr = librosa.load(audio_path, sr=None)
    stats = calculate_physical_stats(y)
    
    mos_score = predict_mos(y, sr)
    
    similarity = 0.0
    if ref_path and os.path.exists(ref_path):
        ref_y, _ = librosa.load(ref_path, sr=sr)
        similarity = calculate_similarity(y, ref_y)
    
    # 総合スコア (100点満点)
    total_score = (mos_score / 5.0 * 60) + (similarity * 40)
    
    return {
        "file": os.path.basename(audio_path),
        "physical_stats": stats,
        "ai_scores": {
            "mos_predicted": round(mos_score, 2),
            "speaker_similarity": round(similarity, 2),
            "total_score": round(total_score, 1)
        }
    }

def main():
    OUTPUT_DIR = "tts_outputs"
    REF_AUDIO = "SOURCE/001.wav"
    STATS_FILE = "OUTPUTS/audio_analysis_stats.txt"
    
    results = []
    
    # tts_outputs 内の wav ファイルをスキャン
    wav_files = list(Path(OUTPUT_DIR).glob("*.wav"))
    if not wav_files:
        print("採点対象のWAVファイルが見つかりません。")
        return

    for wav_path in wav_files:
        score_data = score_audio(str(wav_path), REF_AUDIO)
        results.append(score_data)
        
        print(f"  MOS予測: {score_data['ai_scores']['mos_predicted']}")
        print(f"  類似度: {score_data['ai_scores']['speaker_similarity']}")
        print(f"  総合スコア: {score_data['ai_scores']['total_score']}")

    # 結果をテキストファイルに追記
    with open(STATS_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n--- AI 採点レポート ---\n")
        for res in results:
            f.write(f"\nファイル: {res['file']}\n")
            f.write(f"  MOS予測: {res['ai_scores']['mos_predicted']}/5.0\n")
            f.write(f"  話者類似度: {res['ai_scores']['speaker_similarity']}\n")
            f.write(f"  総合スコア: {res['ai_scores']['total_score']}/100\n")

    print(f"\n採点完了。レポートを {STATS_FILE} に追記しました。")

if __name__ == "__main__":
    main()
