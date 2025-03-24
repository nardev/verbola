import os
import time
import json
import requests
from pydub import AudioSegment
from pydub.generators import Silence

# ==== CONFIG ====
VOICEMAKER_API_KEY = "YOUR_API_KEY_HERE"
VOICEMAKER_API_URL = "https://developer.voicemaker.in/voice/api"

ENGLISH_VOICE = "en-US-JennyNeural"
BOSNIAN_VOICE = "bs-BA-AdisNeural"  # Use appropriate Bosnian voice if available
AUDIO_DIR = "audio_output"
JSON_FILE = "words.json"

os.makedirs(AUDIO_DIR, exist_ok=True)

def generate_audio(text, voice_id, filename):
    payload = {
        "Engine": "neural",
        "LanguageId": "en-US" if 'en' in voice_id else "bs-BA",
        "VoiceId": voice_id,
        "Text": text,
        "OutputFormat": "mp3",
        "SampleRate": "48000",
        "Effect": "default",
        "MasterSpeed": "0",
        "MasterVolume": "0",
        "MasterPitch": "0",
        "Key": VOICEMAKER_API_KEY
    }

    response = requests.post(VOICEMAKER_API_URL, json=payload)
    response.raise_for_status()
    result = response.json()

    if result.get("path"):
        audio_url = result["path"]
        audio_data = requests.get(audio_url)
        with open(filename, "wb") as f:
            f.write(audio_data.content)
        print(f"Saved: {filename}")
    else:
        print("Error:", result)
        raise Exception("Audio path not found in response")

def add_silence(audio_path, duration_ms=500):
    original = AudioSegment.from_file(audio_path)
    silence = Silence(duration=duration_ms).to_audio_segment()
    return silence + original + silence

def main():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        words = json.load(f)

    english_audio_files = []
    bosnian_audio_files = []

    for i, entry in enumerate(words):
        english_word = entry["english"]
        bosnian_word = entry["bosnian"]

        eng_file = os.path.join(AUDIO_DIR, f"{i:03d}_en.mp3")
        bos_file = os.path.join(AUDIO_DIR, f"{i:03d}_bs.mp3")

        generate_audio(english_word, ENGLISH_VOICE, eng_file)
        time.sleep(1)  # Short delay
        generate_audio(bosnian_word, BOSNIAN_VOICE, bos_file)
        time.sleep(1)

        english_audio_files.append(add_silence(eng_file))
        bosnian_audio_files.append(AudioSegment.from_file(bos_file))

    # Combine
    combined = AudioSegment.empty()
    for eng, bos in zip(english_audio_files, bosnian_audio_files):
        combined += eng + bos + Silence(500).to_audio_segment()

    final_path = os.path.join(AUDIO_DIR, "combined_output.mp3")
    combined.export(final_path, format="mp3")
    print(f"\n✅ Final file created: {final_path}")

if __name__ == "__main__":
    main()
