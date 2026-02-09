import sys
import os
import json
import argparse
from pathlib import Path

# Add the current directory to sys.path to ensure imports work
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Add project root to path for importing from src.tools
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

try:
    from src.tools.inspector import Inspector
    from src.tools.diagnostician import Diagnostician
except ImportError as e:
    print(f"Import Error: {e}")
    # Fallback or detailed error message
    print("Please ensure you are running this script with the correct PYTHONPATH or from the project root.")
    sys.exit(1)

def evaluate_audio(audio_path):
    print(f"Evaluating audio: {audio_path}")
    
    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}")
        return

    # 1. Inspection
    print("Running Inspector...")
    try:
        inspector = Inspector()
        inspector_results = inspector.analyze(audio_path)
        print("Inspection complete.")
    except Exception as e:
        print(f"Error during inspection: {e}")
        return

    # 2. Diagnosis
    print("Running Diagnostician...")
    try:
        diagnostician = Diagnostician()
        # linguist_data is optional and currently not implemented in this flow
        report = diagnostician.diagnose(inspector_results)
        print("Diagnosis complete.")
    except Exception as e:
        print(f"Error during diagnosis: {e}")
        return

    # 3. Output
    print("\n" + "="*50)
    print("EVALUATION REPORT")
    print("="*50)
    print(f"Overall Score: {report['overall_score']}/100")
    
    print("\n[Scores]")
    for category, score in report['buckets'].items():
        print(f"  - {category.capitalize()}: {score}")

    print("\n[Highlights]")
    if report['highlights']:
        for highlight in report['highlights']:
            print(f"  ! {highlight}")
    else:
        print("  (None)")

    print("\n[Suggestions]")
    if report['suggestions']:
        for suggestion in report['suggestions']:
            print(f"  > {suggestion}")
    else:
        print("  (None)")
        
    if report.get('lora_recommended'):
        print("\n*** LoRA Fine-tuning Recommended ***")
        print("Quality or Prosody scores are low. Consider training a LoRA adapter.")

    print("="*50)
    
    # Save detailed JSON report
    output_json_path = str(Path(audio_path).with_suffix('.json'))
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "inspection": inspector_results,
            "diagnosis": report
        }, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed report saved to: {output_json_path}")

def main():
    parser = argparse.ArgumentParser(description="Evaluate audio quality and prosody using SNSW tools.")
    parser.add_argument("audio_path", help="Path to the audio file (.wav, .mp3) to evaluate")
    args = parser.parse_args()

    evaluate_audio(args.audio_path)

if __name__ == "__main__":
    main()
