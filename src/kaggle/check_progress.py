import json
import os
import datetime

PROGRESS_FILE = "/kaggle/working/snsw/dev/progress.json"

def check_progress():
    if not os.path.exists(PROGRESS_FILE):
        print("Progress file not found. Training might not have started yet.")
        return

    try:
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
        
        last_update = data.get("last_update", "Unknown")
        phase = data.get("phase", "Unknown")
        status = data.get("status", "Unknown")
        progress = data.get("progress", 0)
        metrics = data.get("metrics", {})

        print("="*40)
        print(f"SNSW Training Progress Report")
        print(f"Last Update: {last_update}")
        print("="*40)
        print(f"Current Phase: {phase}")
        print(f"Status:        {status}")
        bar_fill = min(20, max(0, progress // 5))
        print(f"Overall:       [{'#' * bar_fill}{'.' * (20 - bar_fill)}] {progress}%")
        
        if metrics:
            print("-" * 40)
            print("Metrics/Details:")
            for k, v in metrics.items():
                print(f"  {k}: {v}")
        print("="*40)

    except Exception as e:
        print(f"Error reading progress file: {e}")

if __name__ == "__main__":
    check_progress()
