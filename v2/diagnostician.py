import json
import sys

class Diagnostician:
    def diagnose(self, inspector_data, linguist_data=None):
        # linguist_data がない場合のプレースホルダ
        if linguist_data is None:
            linguist_data = {"cer": 0.0, "mismatches": []}

        q = inspector_data["quality"]
        p = inspector_data["prosody"]
        
        scores = {
            "quality": 100,
            "pronunciation": 100,
            "prosody": 100
        }
        
        highlights = []
        suggestions = []

        # --- Quality Diagnosis ---
        if q["clipping_rate"] > 0.01:
            scores["quality"] -= 30
            highlights.append("Clipping detected (Audio level too high)")
            suggestions.append("Reduce output gain or check vocoder scaling")
        
        if q["spectral_flatness"] > 0.1:
            scores["quality"] -= 20
            highlights.append("High spectral flatness (Metallic or noisy sound)")
            suggestions.append("Check vocoder compatibility or increase diffusion steps")

        # --- Pronunciation Diagnosis ---
        if linguist_data["cer"] > 0.05:
            scores["pronunciation"] -= 40
            highlights.append(f"High Character Error Rate ({linguist_data['cer']:.2%})")
            suggestions.append("Check G2P/Accent dictionary or training data quality")

        # --- Prosody Diagnosis ---
        if p["f0"]["range"] < 50:
            scores["prosody"] -= 20
            highlights.append("Flat intonation (Narrow F0 range)")
            suggestions.append("Increase F0 scale or check emotion embedding")
        
        if p["f0"]["jump_max"] > 150:
            scores["prosody"] -= 25
            highlights.append("Unnatural pitch jump detected")
            suggestions.append("Decrease temperature or check for alignment instability")

        max_silence = max(p["silence_durations"]) if p["silence_durations"] else 0
        if max_silence > 1.0:
            scores["prosody"] -= 15
            highlights.append(f"Long silence detected ({max_silence:.2f}s)")
            suggestions.append("Adjust end-of-sentence silence parameters or trim padding")

        overall = sum(scores.values()) / 3
        
        return {
            "overall_score": round(overall, 1),
            "buckets": scores,
            "highlights": highlights,
            "suggestions": suggestions,
            "lora_recommended": overall < 60 and scores["quality"] < 70
        }

if __name__ == "__main__":
    # Example usage with stdin
    input_data = json.load(sys.stdin)
    diag = Diagnostician()
    report = diag.diagnose(input_data)
    print(json.dumps(report, indent=2))
