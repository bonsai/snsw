import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime
import numpy as np

# インポートパスの設定
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from tools.inspector import Inspector
    from tools.diagnostician import Diagnostician
except ImportError:
    # Docker内などの環境に合わせたフォールバック
    sys.path.append("/app/src")
    from tools.inspector import Inspector
    from tools.diagnostician import Diagnostician

def run_batch_evaluation(target_dir="tts_outputs"):
    print(f"\n--- 一括評価・統計開始: {target_dir} ---")
    
    wav_files = glob.glob(os.path.join(target_dir, "*.wav"))
    if not wav_files:
        print("評価対象のWAVファイルが見つかりません。")
        return

    inspector = Inspector()
    diagnostician = Diagnostician()
    
    results = []
    model_stats = {}

    for wav_path in wav_files:
        try:
            print(f"評価中: {os.path.basename(wav_path)}")
            # モデル名をファイル名から抽出 (例: xtts-audio-...)
            model_name = os.path.basename(wav_path).split('-')[0]
            
            inspector_results = inspector.analyze(wav_path)
            report = diagnostician.diagnose(inspector_results)
            
            score = report['overall_score']
            results.append({
                "file": os.path.basename(wav_path),
                "model": model_name,
                "score": score,
                "buckets": report['buckets'],
                "lora_recommended": report.get('lora_recommended', False),
                "inspector_data": inspector_results
            })

            if model_name not in model_stats:
                model_stats[model_name] = []
            model_stats[model_name].append(score)

        except Exception as e:
            print(f"Error evaluating {wav_path}: {e}")

    # 統計レポート1: モデル選定サマリー (Go/No-Go判断用)
    summary_report_path = os.path.join(target_dir, f"report_1_model_summary_{timestamp}.md")
    # 統計レポート2: 詳細メトリクス一覧 (物理特性・AIスコア)
    detailed_report_path = os.path.join(target_dir, f"report_2_detailed_metrics_{timestamp}.md")
    
    # レポート1の作成
    with open(summary_report_path, "w", encoding="utf-8") as f:
        f.write(f"# レポート1: モデル選定サマリー ({timestamp})\n\n")
        f.write("## モデル別平均スコアと進退判定\n")
        f.write("| モデル | サンプル数 | 平均スコア | 判定 |\n")
        f.write("| :--- | :---: | :---: | :--- |\n")
        for model, scores in model_stats.items():
            avg = np.mean(scores)
            status = "期待大 (学習継続)" if avg > 75 else "見極め中 (LoRA検討)" if avg > 60 else "見限り検討 (要構造見直し)"
            f.write(f"| {model} | {len(scores)} | {avg:.2f} | {status} |\n")
        f.write("\n※ 判断基準は ADR-010 に準拠しています。")

    # レポート2の作成
    with open(detailed_report_path, "w", encoding="utf-8") as f:
        f.write(f"# レポート2: 詳細メトリクス一覧 ({timestamp})\n\n")
        f.write("| ファイル名 | モデル | スコア | 物理特性 (RMS) | LoRA推奨 |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: |\n")
        for res in sorted(results, key=lambda x: x['score'], reverse=True):
            lora = "✅" if res['lora_recommended'] else "-"
            # inspector_results から物理特性を取得
            rms = res.get("inspector_data", {}).get("rms", 0.0)
            f.write(f"| {res['file']} | {res['model']} | {res['score']} | {rms:.4f} | {lora} |\n")

    print(f"\n2種類のレポートを保存しました:\n1. {summary_report_path}\n2. {detailed_report_path}")
    return summary_report_path, detailed_report_path

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "tts_outputs"
    run_batch_evaluation(target)
