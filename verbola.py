import os
import time
from dotenv import load_dotenv
load_dotenv()

import json
import requests
from pydub import AudioSegment

# ==== CONFIG ====
VOICEMAKER_API_KEY = os.getenv("VOICEMAKER_API_KEY")
VOICEMAKER_API_URL = os.getenv("VOICEMAKER_API_URL")

PRIMARY_LANGUAGE = os.getenv("PRIMARY_LANGUAGE")
PRIMARY_LANGUAGE_KEY = os.getenv("PRIMARY_LANGUAGE_KEY")
PRIMARY_LANGUAGE_VOICE = os.getenv("PRIMARY_LANGUAGE_VOICE")
PRIMARY_LANGUAGE_CODE = os.getenv("PRIMARY_LANGUAGE_CODE")

TRANSLATION_LANGUAGE = os.getenv("TRANSLATION_LANGUAGE")
TRANSLATION_LANGUAGE_KEY = os.getenv("TRANSLATION_LANGUAGE_KEY")
TRANSLATION_LANGUAGE_VOICE = os.getenv("TRANSLATION_LANGUAGE_VOICE")
TRANSLATION_LANGUAGE_CODE = os.getenv("TRANSLATION_LANGUAGE_CODE")

AUDIO_DIR = "audio_output"
JSON_FILE = "words.json"

os.makedirs(AUDIO_DIR, exist_ok=True)

def generate_audio(text, voice_id, language_code, filename):
    payload = {
        "Engine": "neural",
        "VoiceId": voice_id,
        "LanguageCode": language_code,
        "Text": text,
        "OutputFormat": "mp3",
        "SampleRate": "48000",
        "Effect": "default",
        "MasterVolume": "0",
        "MasterSpeed": "0",
        "MasterPitch": "0"
    }

    print(json.dumps(payload, indent=2))

    headers = {
        "Authorization": f"Bearer {VOICEMAKER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(VOICEMAKER_API_URL, headers=headers, json=payload)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("🚫 Error:", response.text)
        raise

    result = response.json()

    if result.get("path"):
        audio_url = result["path"]
        audio_data = requests.get(audio_url)
        with open(filename, "wb") as f:
            f.write(audio_data.content)
        print(f"✅ Saved: {filename}")
    else:
        print("❌ Error:", result)
        raise Exception("Audio path not found in response")

def add_silence(audio_path, duration_ms=50):
    original = AudioSegment.from_file(audio_path)
    silence = AudioSegment.silent(duration=duration_ms)
    return silence + original + silence

def main():
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        words = json.load(f)

    primary_lang_audio_files = []
    translate_audio_files = []

    for i, entry in enumerate(words):
        primary = entry[PRIMARY_LANGUAGE]
        translation = entry[TRANSLATION_LANGUAGE]

        primary_lang_text = os.path.join(AUDIO_DIR, f"{i:03d}_{PRIMARY_LANGUAGE}.mp3")
        translate_lang_text = os.path.join(AUDIO_DIR, f"{i:03d}_{TRANSLATION_LANGUAGE}.mp3")

        generate_audio(primary, PRIMARY_LANGUAGE_VOICE, PRIMARY_LANGUAGE_CODE, primary_lang_text)
        time.sleep(1)  #  delay
        generate_audio(translation, TRANSLATION_LANGUAGE_VOICE, TRANSLATION_LANGUAGE_CODE, translate_lang_text)
        time.sleep(1)

        primary_lang_audio_files.append(add_silence(primary_lang_text))
        translate_audio_files.append(AudioSegment.from_file(translate_lang_text))

    # Combine
    combined = AudioSegment.empty()
    for eng, bos in zip(primary_lang_audio_files, translate_audio_files):
        combined += eng + bos + AudioSegment.silent(duration=50)

    final_path = os.path.join(AUDIO_DIR, "combined_output.mp3")
    combined.export(final_path, format="mp3")
    print(f"\n✅ Final file created: {final_path}")

if __name__ == "__main__":
    main()
