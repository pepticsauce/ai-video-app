import streamlit as st
import requests
import tempfile
import os
from pydub import AudioSegment

# -----------------------------
# 🎤 Coqui TTS Endpoint (Free)
# -----------------------------
COQUI_API_URL = "https://app.coqui.ai/api/v2/synthesize"

# -----------------------------
# 🔧 FUNCTIONS
# -----------------------------

def generate_story(prompt, genre, openrouter_api_key):
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = f"You are a Reddit storyteller writing in the genre: {genre}. Write a realistic, emotional, or suspenseful story like you'd find on r/confession or r/nosleep. Use multiple paragraphs."

    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write a Reddit story based on this idea:\n\n{prompt}"}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"OpenRouter Error: {response.text}")


def synthesize_with_coqui(text, voice="Jenny", output_path="output.mp3"):
    # Coqui's public demo endpoint may change, replace with a stable key if needed
    payload = {
        "speaker_id": voice,
        "text": text,
        "emotion": "neutral",
        "speed": 1.0,
    }

    headers = {
        "accept": "audio/mpeg",
        "Content-Type": "application/json"
    }

    response = requests.post(COQUI_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        raise Exception(f"Coqui TTS Error: {response.status_code}: {response.text}")

# -----------------------------
# 🌐 STREAMLIT UI
# -----------------------------

st.set_page_config(page_title="Reddit Story Narrator (Free)", page_icon="📖")
st.title("📖 AI Reddit Story Narrator (MP3 Export)")

openrouter_api_key = st.text_input("🔐 OpenRouter API Key", type="password")
user_prompt = st.text_area("📝 Enter a story idea or prompt", height=100)

genres = ["Mystery", "Sad", "Funny", "Horror", "Romance", "Confession", "Drama"]
selected_genre = st.selectbox("🎭 Choose a story genre", genres)

voices = ["Jenny", "William", "Emma", "Michael"]
selected_voice = st.selectbox("🗣️ Choose a voice (Coqui)", voices)

if openrouter_api_key:
    if st.button("🎙️ Generate Narrated Story"):
        with st.spinner("Generating story and audio..."):
            try:
                # 1. Generate story
                story = generate_story(user_prompt, selected_genre, openrouter_api_key)

                # 2. Generate MP3 using Coqui TTS
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    mp3_path = synthesize_with_coqui(story, voice=selected_voice, output_path=tmp_file.name)

                # 3. Output
                st.success("✅ Narration Ready!")
                st.text_area("📘 Reddit Story", story, height=300)
                audio_bytes = open(mp3_path, "rb").read()
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button("⬇️ Download MP3", audio_bytes, file_name="reddit_story.mp3")

            except Exception as e:
                st.error(f"❌ Error: {e}")
else:
    st.warning("Enter your OpenRouter API key to start.")
