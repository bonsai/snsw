import soundfile as sf
import os

files_to_process = [
    "g:/My Drive/VC/generated_002.wav",
    "g:/My Drive/VC/generated_003.wav"
]

target_duration = 10.0

for file_path in files_to_process:
    # Construct output path
    dir_name = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(dir_name, f"{base_name}_head_10s.wav")
    
    print(f"Processing: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"  ❌ File not found: {file_path}")
        continue

    try:
        data, samplerate = sf.read(file_path)
        duration = len(data) / samplerate
        print(f"  Original Duration: {duration:.2f} seconds")
        
        # Determine cutoff point
        cutoff = int(target_duration * samplerate)
        
        if len(data) > cutoff:
            new_data = data[:cutoff]
            print(f"  Cutting to first {target_duration} seconds...")
        else:
            new_data = data
            print(f"  File is shorter than {target_duration}s, keeping original length.")
            
        sf.write(output_path, new_data, samplerate)
        print(f"  ✓ Saved to: {output_path}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print("-" * 40)
