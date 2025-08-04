import streamlit as st
import requests
import torchaudio
from tortoise.api import TextToSpeech
import tempfile
import os
import torch
from pydub import AudioSegment

# -----------------------------
# 🔧 FUNCTION DEFINITIONS
# -----------------------------

def generate_story(prompt, genre):
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = f"You are a talented Reddit writer crafting stories in the {genre} genre. Make it feel like a real post from r/confession or r/nosleep."

    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write a detailed, engaging Reddit post in the style of {genre}. Use this idea:\n\n{prompt}"}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"OpenRouter Error: {response.text}")


def generate_tortoise_audio(text, voice='daniel', output_path='output.mp3'):
    tts = TextToSpeech()
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    
    combined_audio = None
    sample_rate = 24000
    for idx, para in enumerate(paragraphs):
        with torch.inference_mode():
            audio_tensor = tts.tts(para, voice=voice, preset='fast')
        if combined_audio is None:
            combined_audio = audio_tensor
        else:
            silence = torch.zeros(1, int(sample_rate * 0.75))  # 0.75 sec pause
            combined_audio = torch.cat([combined_audio, silence, audio_tensor], dim=1)

    # Save as WAV
    wav_temp_path = tempfile.mktemp(suffix=".wav")
    torchaudio.save(wav_temp_path, combined_audio.squeeze(0).cpu(), sample_rate)

    # Convert to MP3
    audio = AudioSegment.from_wav(wav_temp_path)
    mp3_path = wav_temp_path.replace(".wav", ".mp3")
    audio.export(mp3_path, format="mp3")

    return mp3_path

# -----------------------------
# 🌐 STREAMLIT UI
# -----------------------------

st.set_page_config(page_title="AI Reddit Story Audio", page_icon="🎙️")
st.title("🎙️ AI Reddit Story Generator (Tortoise TTS, MP3 Output)")

openrouter_api_key = st.text_input("🔑 OpenRouter API Key", type="password")
user_prompt = st.text_area("💡 Enter a story prompt", height=100)

# 🎭 Genre Selection
genres = ["Mystery", "Sad", "Funny", "Horror", "Romance", "Confession", "Drama"]
selected_genre = st.selectbox("🎭 Choose Story Genre", genres)

# 🎤 Voice Selection
available_voices = ["daniel", "emma", "lj", "rainbow", "train_dreams", "tom", "deniro"]
selected_voice = st.selectbox("🎤 Choose Tortoise Voice", available_voices)

if openrouter_api_key:
    if st.button("📝 Generate Story and Narrate"):
        with st.spinner("Generating story and audio..."):
            try:
                story = generate_story(user_prompt, selected_genre)
                mp3_path = generate_tortoise_audio(story, voice=selected_voice)

                st.success("✅ Audio Ready!")
                st.text_area("📖 Generated Story", story, height=300)
                with open(mp3_path, "rb") as f:
                    audio_data = f.read()
                    st.audio(audio_data, format="audio/mp3")
                    st.download_button("⬇️ Download MP3", audio_data, file_name="reddit_story.mp3")

            except Exception as e:
                st.error(f"❌ Error: {e}")
else:
    st.info("Please enter your OpenRouter API key to begin.")
