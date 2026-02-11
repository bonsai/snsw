# Docker 環境での実行ガイド

このプロジェクトを Docker 環境で実行するためのガイドです。GPU を使用して高速に音声合成・変換を行うことができます。

## 前提条件

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) または Docker Engine がインストールされていること。
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) がインストールされていること（GPU を使用する場合）。

## クイックスタート

### 1. イメージのビルド

```bash
docker-compose build
```

### 2. 推論の実行

`docker-compose run` を使用して、コンテナ内で推論スクリプトを実行します。

```bash
docker-compose run snsw-ai --text "えー、お馴染みの一席でございます。" --speaker_wav data/ref_shinsho.wav --output outputs/docker_out.wav
```

## Tips

- **モデルの永続化**: モデルデータは Docker ボリューム `snsw-models` に保存されるため、コンテナを削除しても再ダウンロードは不要です。
- **GPU の確認**: コンテナ内で `nvidia-smi` を実行して GPU が認識されているか確認できます。
  ```bash
  docker-compose run snsw-ai nvidia-smi
  ```

## Windows (PowerShell) での実行例

```powershell
docker-compose run snsw-ai `
    --text "志ん生でございます。" `
    --speaker_wav "data/ref_shinsho.wav" `
    --output "outputs/docker_out.wav"
```
