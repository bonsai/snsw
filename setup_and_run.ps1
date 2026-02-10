# 五代目古今亭志ん生 音声再現プロジェクト - 環境構築 & 実行スクリプト

$VENV_NAME = ".venv"

# 1. 仮想環境の作成とライブラリのインストール
Write-Host "--- Step 1: Setting up Python Virtual Environment ---" -ForegroundColor Cyan
if (!(Test-Path $VENV_NAME)) {
    python -m venv $VENV_NAME
}

# 仮想環境のアクティベート
$ActivateScript = if ($IsWindows) { "$VENV_NAME\Scripts\Activate.ps1" } else { "$VENV_NAME/bin/Activate.ps1" }
. $ActivateScript

# 依存ライブラリのインストール
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -U pip
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install TTS peft transformers datasets safetensors

# 2. 推論の実行例
Write-Host "`n--- Step 2: Running Hybrid Inference ---" -ForegroundColor Cyan

$Text = "えー、お馴染みの一席でございます。志ん生でございます。"
$SpeakerWav = "data/ref_shinsho.wav"
$LoraPath = "outputs/xtts_lora_shinsho"
$RvcModel = "models/rvc/shinsho.pth"
$OutputPath = "outputs/final_voice.wav"

# フォルダの作成
if (!(Test-Path "outputs")) { New-Item -ItemType Directory "outputs" }

Write-Host "Starting hybrid synthesis..." -ForegroundColor Green
python hybrid_inference.py `
    --text $Text `
    --speaker_wav $SpeakerWav `
    --lora_path $LoraPath `
    --rvc_model $RvcModel `
    --output $OutputPath

Write-Host "`nDone! Output saved to: $OutputPath" -ForegroundColor Green
