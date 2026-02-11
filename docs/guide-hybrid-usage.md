# ハイブリッド推論ガイド (XTTS-v2 + RVC)

このガイドでは、XTTS-v2の表現力とRVCの音色再現を組み合わせた「ハイブリッド推論」の実行方法を説明します。

## 概要
1. **XTTS-v2**: 入力テキストから、感情や抑揚を含んだ音声を生成します。
2. **RVC**: XTTS-v2で生成された音声の音色を、五代目古今亭志ん生の特定の声質に変換します。

## 実行方法

### Docker を使用する場合
```bash
docker-compose run --rm snsw-ai python src/hybrid_inference.py \
    --text "えー、お馴染みの一席でございます。志ん生でございます。" \
    --speaker_wav /app/audio-source/001.wav \
    --rvc_model /app/models/shinsho_rvc.pth \
    --output /app/tts_outputs/hybrid_shinsho.wav
```

### パラメータ
- `--text`: 合成したいテキスト
- `--speaker_wav`: XTTS-v2の参照用音声（抑揚のベースになります）
- `--xtts_model`: ファインチューニング済みのXTTSモデルを使用する場合に指定
- `--rvc_model`: RVCのモデルファイル (.pth) のパス
- `--output`: 出力先パス

## モデルの配置
- RVCモデル (.pth) は `models/` ディレクトリに配置することを推奨します。
- 生成された音声は `tts_outputs/` に保存されます。
