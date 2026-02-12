# -*- coding: utf-8 -*-
import os
from huggingface_hub import snapshot_download

def download_moondream():
    print("\n--- moondream モデルのダウンロード ---")
    repo_id = "vikhyatk/moondream2"
    # Revision を指定して安定したバージョンを取得（必要に応じて最新に変更可能）
    revision = "2025-01-09" 
    local_dir = "C:/models/vlm/moondream2"
    
    print(f"Repo ID: {repo_id}")
    print(f"Local Dir: {local_dir}")
    
    try:
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
            
        print("ダウンロードを開始します。これには時間がかかる場合があります...")
        snapshot_download(
            repo_id=repo_id,
            revision=revision,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        print("\nダウンロードが完了しました！")
        print(f"場所: {local_dir}")
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")

if __name__ == "__main__":
    download_moondream()
