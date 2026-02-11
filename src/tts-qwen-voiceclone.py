# Qwen4-TTS Voice Clone POC
# シンプルな音声クローニング実装
# 3秒程度の参照音声から声をクローンして、任意のテキストを読み上げます。

# 必要なライブラリのインストール
# !pip install -q qwen-tts soundfile torch torchaudio

import torch
import soundfile as sf
import numpy as np
import os
import time
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from qwen_tts import Qwen3TTSModel

# デバイス設定
device = "cuda:0" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

print(f"✓ デバイス: {device}")
print(f"✓ データ型: {dtype}")

# モデルのロード
print("モデルをロード中...")
try:
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-0.5B",
        device=device,
        dtype=dtype
    )
    print("✓ モデルロード完了")
except Exception as e:
    print(f"❌ モデルのロードに失敗しました: {e}")
    print("Hugging Faceの認証が必要な場合があります。")
    exit(1)

# ファイルパスの設定
# Google Driveのマウント（Colab環境の場合）
try:
    from google.colab import drive
    drive.mount('/content/drive')
    base_path = '/content/drive/MyDrive'
    print("✓ Google Drive マウント完了")
except:
    # ローカル環境の場合
    base_path = '.'
    print("✓ ローカル環境で実行")

# ファイルパス設定
reference_audio = "001.wav"  # 参照音声ファイル
output_dir = os.path.join(base_path, "tts_outputs")
os.makedirs(output_dir, exist_ok=True)

print(f"参照音声: {reference_audio}")
print(f"出力先: {output_dir}")

# 参照音声ファイルの存在確認と情報表示
if os.path.exists(reference_audio):
    audio_data, sr = sf.read(reference_audio)
    duration = len(audio_data) / sr
    print(f"✓ 参照音声ファイル確認完了")
    print(f"  - サンプリングレート: {sr} Hz")
    print(f"  - 長さ: {duration:.2f} 秒")
    print(f"  - チャンネル数: {audio_data.ndim}")
    
    # 参照音声を再生 (スクリプト環境では再生不可のためコメントアウト)
    # from IPython.display import Audio, display
    # display(Audio(reference_audio))
else:
    print(f"❌ エラー: {reference_audio} が見つかりません")
    print("ファイルパスを確認してください")

def generate_with_timeout(model, text, prompt_audio_path, speed=1.0, timeout=600):
    """
    タイムアウト機能付きの音声生成関数
    
    Args:
        model: Qwen3TTSModel インスタンス
        text: 生成するテキスト
        prompt_audio_path: 参照音声のパス
        speed: 再生速度（デフォルト: 1.0）
        timeout: タイムアウト時間（秒）（デフォルト: 600秒 = 10分）
    
    Returns:
        generated_audio: 生成された音声データ
    
    Raises:
        TimeoutError: 生成時間がタイムアウトを超えた場合
    """
    def _generate():
        return model.generate(
            text=text,
            prompt_audio_path=prompt_audio_path,
            speed=speed
        )
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_generate)
        try:
            result = future.result(timeout=timeout)
            return result
        except TimeoutError:
            print(f"❌ エラー: 音声生成が{timeout}秒を超えました")
            raise

def check_audio_duration(audio_data, sample_rate, max_duration=60):
    """
    音声の長さをチェックする関数
    
    Args:
        audio_data: 音声データ（numpy配列）
        sample_rate: サンプリングレート
        max_duration: 最大長さ（秒）（デフォルト: 60秒）
    
    Returns:
        duration: 音声の長さ（秒）
        is_valid: 最大長さ以内かどうか
    """
    duration = len(audio_data) / sample_rate
    is_valid = duration <= max_duration
    
    if is_valid:
        print(f"✓ 音声長: {duration:.2f}秒 (制限: {max_duration}秒以内)")
    else:
        print(f"⚠ 警告: 音声長 {duration:.2f}秒が制限({max_duration}秒)を超えています")
    
    return duration, is_valid

# text.jsonの読み込み
json_filename = "text.json"
json_path = os.path.join(base_path, json_filename) if 'base_path' in globals() else json_filename

if not os.path.exists(json_path):
    print(f"❌ Error: {json_path} not found.")
    # ダミーデータ作成
    sample_data = [{"id": "001", "text": "これはテスト生成です。"}]
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=4)
    print(f"Created sample {json_path}")

with open(json_path, 'r', encoding='utf-8') as f:
    text_data = json.load(f)

print("="*60)
print(f"音声生成バッチ処理を開始します ({len(text_data)} items)")
print("="*60)

generated_audio = None # 最後の生成音声を保持

for item in text_data:
    item_id = item.get("id", "unknown")
    text = item.get("text", "")
    
    if not text:
        continue
        
    print(f"\n[ID: {item_id}] Processing...")
    print(f"Text: {text[:50]}...\" if len(text) > 50 else f\"Text: {text}")
    
    start_time = time.time()
    try:
        # 音声生成
        current_audio = generate_with_timeout(
            model=model,
            text=text,
            prompt_audio_path=reference_audio,
            speed=1.0,
            timeout=600
        )
        
        generation_time = time.time() - start_time
        generated_audio = current_audio
        
        # 保存
        filename = f"generated_{item_id}.wav"
        output_path = os.path.join(output_dir, filename)
        sf.write(output_path, current_audio, model.sample_rate)
        
        print(f"✓ Generated in {generation_time:.2f}s")
        print(f"✓ Saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Failed to generate for ID {item_id}: {e}")
        import traceback
        traceback.print_exc()

print("\nAll items processed.")

# 詳細な音声分析（オプション）
try:
    import librosa
    import librosa.display
    import matplotlib.pyplot as plt
    
    if generated_audio is not None:
        print("\n音声分析を開始します...")
        # 波形表示
        plt.figure(figsize=(14, 5))
        plt.subplot(2, 1, 1)
        librosa.display.waveshow(generated_audio, sr=model.sample_rate)
        plt.title('生成音声の波形')
        plt.xlabel('時間 (秒)')
        plt.ylabel('振幅')
        
        # スペクトログラム表示
        plt.subplot(2, 1, 2)
        D = librosa.amplitude_to_db(np.abs(librosa.stft(generated_audio)), ref=np.max)
        librosa.display.specshow(D, sr=model.sample_rate, x_axis='time', y_axis='hz')
        plt.colorbar(format='%+2.0f dB')
        plt.title('スペクトログラム')
        
        plt.tight_layout()
        # plt.show() # スクリプト実行時はウィンドウを閉じないと進まないため保存に変更
        plt.savefig(os.path.join(output_dir, 'audio_analysis.png'))
        print(f"✓ 分析画像を保存しました: {os.path.join(output_dir, 'audio_analysis.png')}")
        
        # 統計情報
        print("\n音声統計情報:")
        print(f"  平均振幅: {np.mean(np.abs(generated_audio)):.6f}")
        print(f"  最大振幅: {np.max(np.abs(generated_audio)):.6f}")
        print(f"  RMS: {np.sqrt(np.mean(generated_audio**2)):.6f}")
    else:
        print("音声が生成されていません")
        
except ImportError:
    print("\nlibrosa または matplotlib がインストールされていないため、詳細分析をスキップします。")
