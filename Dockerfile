# NVIDIA CUDA 11.8 搭載の PyTorch イメージをベースにする
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# 環境変数の設定
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# 依存ライブラリのインストール
# まずは基本的な依存関係をインストール
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# XTTS-v2, RVC関連のライブラリをインストール
RUN pip install --no-cache-dir \
    TTS \
    peft \
    transformers==4.35.2 \
    datasets \
    safetensors \
    scipy \
    librosa \
    faster-whisper \
    yt-dlp

# アプリケーションコードのコピー
COPY . .

# モデルキャッシュディレクトリの作成と権限設定
RUN mkdir -p /root/.cache/torch/hub/checkpoints && \
    mkdir -p /app/models && \
    mkdir -p /app/tts_outputs

# 実行コマンド（デフォルトはヘルプ表示）
ENTRYPOINT ["python"]
CMD ["src/kaggle/run_inference.py", "--help"]
