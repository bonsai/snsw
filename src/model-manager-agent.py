# -*- coding: utf-8 -*-
import os
import json
import subprocess
import sys

class ModelManagerAgent:
    """
    システムの全AIモデルの管理（レジストリ）とダウンロードを統合して担当するエージェント
    """
    def __init__(self, json_path=None):
        # src/models.json をデフォルトの保存先とする
        if json_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.json_path = os.path.join(base_dir, "models.json")
        else:
            self.json_path = os.path.abspath(json_path)
            
        self.registry = self.load_registry()

    def load_registry(self):
        """JSONファイルからレジストリを読み込む。"""
        if not os.path.exists(self.json_path):
            print(f"[!] Error: {self.json_path} not found.")
            print(f"    Please ensure the models.json file exists in the same directory.")
            return {}

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[!] Error: Failed to parse {self.json_path} (Invalid JSON format): {e}")
            return {}
        except Exception as e:
            print(f"[!] Error: Failed to load {self.json_path}: {e}")
            return {}

    def save_registry(self):
        """現在のレジストリをJSONファイルに保存する。"""
        try:
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
            print(f">>> Registry saved to {self.json_path}")
            return True
        except Exception as e:
            print(f"[!] Failed to save registry: {e}")
            return False

    def get_model_info(self, key):
        return self.registry.get(key)

    def resolve_path(self, key, environment="container"):
        info = self.get_model_info(key)
        if not info: return None
        return info.get("container_path") if environment == "container" else info.get("local_path")

    def download_all(self):
        """登録されているすべてのモデル（manual以外）をダウンロードする。"""
        print(f">>> Starting comprehensive model downloads...")
        for key in self.registry:
            self.download_model(key)
        print(">>> All downloads completed.")

    def download_model(self, key):
        """特定のモデルをダウンロードする。"""
        model = self.get_model_info(key)
        if not model:
            print(f"[!] Model key '{key}' not found.")
            return

        name = model.get("name", key)
        m_type = model.get("type", "manual")
        dest = model.get("container_path")
        remote_url = model.get("remote_url")
        hf_id = model.get("huggingface_id")

        if m_type == "manual":
            print(f"[*] Skipping {name} (Manual installation: {remote_url})")
            return

        print(f">>> Processing {name} ({m_type})...")
        try:
            if m_type == "huggingface":
                target_id = hf_id if hf_id and hf_id != "various" else remote_url
                subprocess.run(["python3", "-c", f"from huggingface_hub import snapshot_download; snapshot_download(repo_id='{target_id}', local_dir='{dest}')"], check=True)

            elif m_type == "direct_download":
                filename = remote_url.split("/")[-1].split("?")[0]
                os.makedirs(dest, exist_ok=True)
                subprocess.run(["curl", "-L", remote_url, "-o", f"{dest}/{filename}"], check=True)

            elif m_type == "tts_api":
                target_id = hf_id if hf_id else remote_url
                subprocess.run(["python3", "-c", f"from TTS.api import TTS; TTS(model_name='{target_id}')"], check=True)

            elif m_type == "whisper_api":
                target_id = hf_id if hf_id else remote_url
                subprocess.run(["python3", "-c", f"from faster_whisper import WhisperModel; WhisperModel('{target_id}', device='cpu', compute_type='int8')"], check=True)
            
            print(f"    [OK] {name} is ready.")
        except Exception as e:
            print(f"    [ERROR] Failed to download {name}: {e}")

if __name__ == "__main__":
    # CLI interface
    agent = ModelManagerAgent()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "download-all":
            agent.download_all()
        elif cmd == "download" and len(sys.argv) > 2:
            agent.download_model(sys.argv[2])
        elif cmd == "list":
            print(json.dumps(agent.registry, indent=2, ensure_ascii=False))
        elif cmd == "save":
            agent.save_registry()
    else:
        print("Usage: python model-manager-agent.py [download-all | download <key> | list | save]")
        # デフォルト動作としてリストを表示
        print("\n--- Current Registry ---")
        for k, v in agent.registry.items():
            print(f"- {k}: {v.get('name')} ({v.get('type')})")
