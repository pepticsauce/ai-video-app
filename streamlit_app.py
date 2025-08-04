import streamlit as st
import requests
from elevenlabs import generate, save, set_api_key

# -----------------------------
# 🔧 FUNCTION DEFINITIONS
# -----------------------------

def generate_story(prompt):
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a Reddit user who writes original and emotional or suspenseful stories for r/confession or r/nosleep."},
            {"role": "user", "content": f"Write a detailed, engaging Reddit post story based on this idea:\n\n{prompt}"}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"OpenRouter Error: {response.text}")


def text_to_speech(text, voice, filename="story.mp3"):
    set_api_key(elevenlabs_api_key)
    audio = generate(
        text=text,
        voice=voice,
        model='eleven_multilingual_v2'
    )
    save(audio, filename)
    return filename

# -----------------------------
# 🌐 STREAMLIT UI
# -----------------------------

st.set_page_config(page_title="AI Reddit Story Generator", page_icon="🎙️")
st.title("🎙️ AI Reddit Story Audio Generator")

# 🔐 API Keys
openrouter_api_key = st.text_input("🔑 OpenRouter API Key", type="password")
elevenlabs_api_key = st.text_input("🎤 ElevenLabs API Key", type="password")

# 🔊 Voice selection
available_voices = [
    "Rachel", "Domi", "Bella", "Antoni", "Elli",
    "Josh", "Arnold", "Adam", "Sam"
]
selected_voice = st.selectbox("🎤 Choose a voice", available_voices, index=0)

# 📝 Prompt input and generate button
if openrouter_api_key and elevenlabs_api_key:
    user_prompt = st.text_area("💡 Enter a story prompt (e.g., 'A man confesses something terrible from his childhood')", height=100)

    if st.button("📝 Generate Story and Narrate"):
        with st.spinner("Generating story and audio..."):
            try:
                story = generate_story(user_prompt)
                audio_file = text_to_speech(story, selected_voice)

                st.success("✅ Audio Ready!")
                st.text_area("📖 Generated Story", story, height=300)
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button("⬇️ Download MP3", audio_bytes, file_name="reddit_story.mp3")

            except Exception as e:
                st.error(f"❌ Error: {e}")
else:
    st.info("Please enter both API keys to begin.")
