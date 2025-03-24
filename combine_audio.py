import os
from pydub import AudioSegment

AUDIO_DIR = "audio_output"
FINAL_FILE = os.path.join(AUDIO_DIR, "combined_output.mp3")
PAUSE_MS = 50

# Collect file pairs
file_pairs = []
for file in sorted(os.listdir(AUDIO_DIR)):
    if file.endswith("_en.mp3"):
        index = file.split("_")[0]
        en_path = os.path.join(AUDIO_DIR, f"{index}_en.mp3")
        bs_path = os.path.join(AUDIO_DIR, f"{index}_bs.mp3")
        if os.path.exists(en_path) and os.path.exists(bs_path):
            file_pairs.append((en_path, bs_path))

# Combine
combined = AudioSegment.empty()
for index, (en_file, bs_file) in enumerate(file_pairs):
    print(f"✅ Joining file: {index}")
    en_audio = AudioSegment.from_file(en_file)
    bs_audio = AudioSegment.from_file(bs_file)
    combined += en_audio + AudioSegment.silent(duration=PAUSE_MS) + bs_audio + AudioSegment.silent(duration=PAUSE_MS)

# Export
combined.export(FINAL_FILE, format="mp3")
print(f"✅ Combined file created: {FINAL_FILE}")
