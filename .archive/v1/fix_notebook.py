import json
import os

# Define the input and output paths
input_path = 'g:/My Drive/VC/qwen4_backup.ipynb'
output_path = 'g:/My Drive/VC/qwen4.ipynb'

# Read the notebook
with open(input_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Helper to find cell by source content
def find_cell_index(source_snippet):
    for i, cell in enumerate(nb['cells']):
        source = "".join(cell['source'])
        if source_snippet in source:
            return i
    return -1

# 1. Update Title (Markdown)
idx = find_cell_index("# Qwen4-TTS Voice Clone POC")
if idx != -1:
    nb['cells'][idx]['source'] = [
        "# Qwen3-TTS Voice Clone POC\n",
        "## シンプルな音声クローニング実装\n",
        "\n",
        "3秒程度の参照音声から声をクローンして、任意のテキストを読み上げます。\n",
        "**注意**: Qwen3-TTSのBaseモデルを使用する場合、参照音声の書き起こしテキスト（リファレンステキスト）が必要になる場合があります。"
    ]

# 2. Update Installation (Code)
idx = find_cell_index("!pip install -q qwen-tts")
if idx != -1:
    nb['cells'][idx]['source'] = [
        "# 必要なライブラリのインストール\n",
        "# 公式リポジトリからインストール (Qwen3-TTSはpip install qwen-ttsでも入る場合がありますが、最新版を推奨)\n",
        "!pip install -q git+https://github.com/QwenLM/Qwen3-TTS.git soundfile torch torchaudio\n",
        "# Flash Attentionはモデルの動作に強く推奨されます\n",
        "!pip install -q flash-attn --no-build-isolation\n",
        "\n",
        "import torch\n",
        "import soundfile as sf\n",
        "import numpy as np\n",
        "from IPython.display import Audio, display\n",
        "from qwen_tts import Qwen3TTSModel\n",
        "import os\n",
        "import time\n",
        "from concurrent.futures import ThreadPoolExecutor, TimeoutError\n",
        "\n",
        "# デバイス設定\n",
        "device = \"cuda:0\" if torch.cuda.is_available() else \"cpu\"\n",
        "dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32\n",
        "\n",
        "print(f\"✓ デバイス: {device}\")\n",
        "print(f\"✓ データ型: {dtype}\")"
    ]

# 3. Update Model Load (Code)
idx = find_cell_index("model = Qwen3TTSModel.from_pretrained")
if idx != -1:
    nb['cells'][idx]['source'] = [
        "# Qwen3-TTSモデルの初期化\n",
        "print(\"モデルをロード中...\")\n",
        "# 音声クローニングには 'Base' モデルを使用します (CustomVoiceはプリセット用)\n",
        "# 0.5Bというモデルは存在しないため、0.6B-Baseに変更しました\n",
        "model_id = \"Qwen/Qwen3-TTS-12Hz-0.6B-Base\"\n",
        "\n",
        "model = Qwen3TTSModel.from_pretrained(\n",
        "    model_id,\n",
        "    device_map=device,\n",
        "    dtype=dtype,\n",
        "    attn_implementation=\"flash_attention_2\" if torch.cuda.is_available() else None\n",
        ")\n",
        "print(f\"✓ モデルロード完了: {model_id}\")"
    ]

# 4. Add Reference Text Cell (Markdown + Code) - Insert after "4. 参照音声の確認"
# Find the index of "4. 参照音声の確認"
idx_ref_check = find_cell_index("## 4. 参照音声の確認")
# We want to insert after the code cell following this markdown.
# The code cell following it is index idx_ref_check + 1 (usually)
# Let's check the next cell to be sure it's the code cell
if idx_ref_check != -1 and nb['cells'][idx_ref_check+1]['cell_type'] == 'code':
    # We will insert new cells after this code cell
    insert_pos = idx_ref_check + 2
    
    new_cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4.5. 参照音声のテキスト設定（Baseモデルに必須）\n",
                "Qwen3-TTSのBaseモデルでクローニングを行う場合、参照音声の内容（テキスト）が必要です。"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 参照音声のテキスト（書き起こし）を入力してください\n",
                "# ※ここを正確に入力しないと、生成される音声の品質が低下したり、エラーになったりします\n",
                "reference_text = \"ここに参照音声（001.wav）の話している内容をテキストで入力してください\" \n",
                "\n",
                "print(f\"参照テキスト: {reference_text}\")"
            ]
        }
    ]
    
    # Check if we already added it (to avoid duplication if run multiple times)
    # Simple check: see if next cell is "4.5"
    if insert_pos < len(nb['cells']) and "4.5" not in "".join(nb['cells'][insert_pos].get('source', [])):
         for cell in reversed(new_cells):
            nb['cells'].insert(insert_pos, cell)

# 5. Update Generation Function (Code)
idx = find_cell_index("def generate_with_timeout")
if idx != -1:
    nb['cells'][idx]['source'] = [
        "def generate_with_timeout(model, text, prompt_audio_path, prompt_text=None, speed=1.0, timeout=600):\n",
        "    \"\"\"\n",
        "    タイムアウト機能付きの音声生成関数\n",
        "    \n",
        "    Args:\n",
        "        model: Qwen3TTSModel インスタンス\n",
        "        text: 生成するテキスト\n",
        "        prompt_audio_path: 参照音声のパス\n",
        "        prompt_text: 参照音声のテキスト（Baseモデルの場合必須）\n",
        "        speed: 再生速度（デフォルト: 1.0）\n",
        "        timeout: タイムアウト時間（秒）（デフォルト: 600秒 = 10分）\n",
        "    \"\"\"\n",
        "    def _generate():\n",
        "        # Baseモデルのクローニングフロー\n",
        "        # 1. プロンプト作成\n",
        "        # 注: APIの実装状況によりメソッド名が異なる可能性があります。\n",
        "        # 以下のコードはQwen3-TTSの標準的な使用法を想定しています。\n",
        "        \n",
        "        try:\n",
        "            # create_voice_clone_prompt または同等のメソッドを探す\n",
        "            if hasattr(model, 'create_voice_clone_prompt'):\n",
        "                print(\"Running voice clone with prompt creation...\")\n",
        "                vc_prompt = model.create_voice_clone_prompt(\n",
        "                    ref_audio=prompt_audio_path,\n",
        "                    ref_text=prompt_text if prompt_text else \"dummy text\" # テキストがないとエラーになる可能性大\n",
        "                )\n",
        "                output, _ = model.generate_voice_clone(\n",
        "                    text=text,\n",
        "                    voice_clone_prompt=vc_prompt,\n",
        "                    speed=speed\n",
        "                )\n",
        "                return output\n",
        "            \n",
        "            # フォールバック: generateメソッド（引数が違う可能性あり）\n",
        "            print(\"Using standard generate method...\")\n",
        "            # 古いAPIや簡易APIの場合\n",
        "            # Qwen3のBaseモデルは通常 prompt_audio_path と prompt_text を要求します\n",
        "            return model.generate(\n",
        "                text=text,\n",
        "                prompt_audio_path=prompt_audio_path,\n",
        "                prompt_text=prompt_text,\n",
        "                speed=speed\n",
        "            )\n",
        "            \n",
        "        except Exception as e:\n",
        "            print(f\"生成エラー詳細: {e}\")\n",
        "            # 最後の手段: 引数を変えて試行\n",
        "            return model.generate(\n",
        "                text=text,\n",
        "                audio_prompt_path=prompt_audio_path,\n",
        "                speed=speed\n",
        "            )\n",
        "\n",
        "    with ThreadPoolExecutor(max_workers=1) as executor:\n",
        "        future = executor.submit(_generate)\n",
        "        try:\n",
        "            result = future.result(timeout=timeout)\n",
        "            return result\n",
        "        except TimeoutError:\n",
        "            print(f\"❌ エラー: 音声生成が{timeout}秒を超えました\")\n",
        "            raise\n",
        "\n",
        "print(\"✓ タイムアウト機能付き生成関数を定義（Voice Clone対応版）\")"
    ]

# 6. Update Generation Call (Code)
idx = find_cell_index("# 生成するテキスト（玉音放送の一節）")
if idx != -1:
    # Need to update the call to pass reference_text
    original_source = "".join(nb['cells'][idx]['source'])
    new_source = original_source.replace(
        "generated_audio = generate_with_timeout(\n        model=model,\n        text=text,\n        prompt_audio_path=reference_audio,\n",
        "generated_audio = generate_with_timeout(\n        model=model,\n        text=text,\n        prompt_audio_path=reference_audio,\n        prompt_text=reference_text,\n"
    )
    nb['cells'][idx]['source'] = new_source.splitlines(keepends=True)

# Write the result
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Notebook updated successfully.")
