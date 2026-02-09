# NVIDIA CUDA 11.8 搭載の PyTorch イメージをベースにする
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# 依存ライブラリのインストール
# XTTS-v2, RVC関連のライブラリをインストール
RUN pip install --no-cache-dir \
    TTS \
    peft \
    transformers \
    datasets \
    safetensors \
    scipy \
    librosa

# アプリケーションコードのコピー
COPY . .

# モデルキャッシュディレクトリの作成
RUN mkdir -p /root/.cache/torch/hub/checkpoints

# 実行コマンド（デフォルトはヘルプ表示）
ENTRYPOINT ["python", "hybrid_inference.py"]
CMD ["--help"]
