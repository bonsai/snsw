---
name: "wav2mp3"
description: "Converts WAV audio files to MP3 format using ffmpeg. Invoke when the user wants to convert audio files or specifically asks for wav to mp3 conversion."
---

# WAV to MP3 Converter

This skill converts WAV audio files to MP3 format using `ffmpeg`.

## Usage

When the user asks to convert a WAV file to MP3, use the `ffmpeg` command.

### Command Template

```bash
ffmpeg -i "<input_file.wav>" "<output_file.mp3>"
```

### Notes
- Ensure the input file path is correct.
- If no output filename is specified, use the same basename as the input file but with the `.mp3` extension.
- Verify the conversion was successful by checking the exit code.
