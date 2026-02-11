import numpy as np
import librosa
import json
import sys

class Inspector:
    def __init__(self, sample_rate=24000):
        self.sr = sample_rate

    def analyze(self, audio_path):
        y, sr = librosa.load(audio_path, sr=self.sr)
        
        # 1. Quality Metrics
        # Clipping detection
        clipping_rate = np.sum(np.abs(y) >= 0.99) / len(y)
        
        # SNR estimation (simplified)
        stft = np.abs(librosa.stft(y))
        noise_floor = np.percentile(stft, 10)
        signal_power = np.mean(stft**2)
        snr = 10 * np.log10(signal_power / (noise_floor**2 + 1e-10))
        
        # Spectral Flatness (higher means more noise-like)
        flatness = np.mean(librosa.feature.spectral_flatness(y=y))

        # 2. Prosody Metrics (F0)
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        f0_clean = f0[~np.isnan(f0)]
        
        f0_stats = {
            "mean": float(np.mean(f0_clean)) if len(f0_clean) > 0 else 0,
            "std": float(np.std(f0_clean)) if len(f0_clean) > 0 else 0,
            "range": float(np.max(f0_clean) - np.min(f0_clean)) if len(f0_clean) > 0 else 0,
            "jump_max": float(np.max(np.abs(np.diff(f0_clean)))) if len(f0_clean) > 1 else 0
        }

        # 3. Silence / Rhythm
        intervals = librosa.effects.split(y, top_db=30)
        silence_durations = []
        last_end = 0
        for start, end in intervals:
            if start > last_end:
                silence_durations.append((start - last_end) / sr)
            last_end = end
        
        return {
            "quality": {
                "clipping_rate": float(clipping_rate),
                "snr_est": float(snr),
                "spectral_flatness": float(flatness)
            },
            "prosody": {
                "f0": f0_stats,
                "silence_durations": silence_durations,
                "total_duration": float(len(y) / sr)
            }
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 inspector.py <audio_path>")
        sys.exit(1)
    
    inspector = Inspector()
    results = inspector.analyze(sys.argv[1])
    print(json.dumps(results, indent=2))
