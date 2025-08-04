import streamlit as st
from gtts import gTTS
import tempfile
import os
import requests

# 🌐 Set your OpenRouter API key
OPENROUTER_API_KEY = st.text_input("🔑 OpenRouter API Key", type="password")

# 🎙️ Choose voice option
voice_option = st.selectbox("🎤 Choose voice type", ["Default (gTTS)", "British (gTTS)", "Australian (gTTS)"])

# 🎭 Choose story genre
genre = st.selectbox("🎭 Choose a genre", ["Default", "Horror", "Romance", "Funny", "Mystery", "Sci-Fi"])

# 📝 Story prompt
prompt = st.text_area("💡 Enter a story prompt or theme:", placeholder="e.g. time travel, haunted house, secret admirer...")

# -----------------------------
# 🔧 FUNCTIONS
# -----------------------------

def generate_story_with_openrouter(prompt, genre):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a master storyteller. Write Reddit-style stories based on genre."},
            {"role": "user", "content": f"Write a 3-paragraph story in the genre '{genre}' using this prompt: {prompt}"}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"OpenRouter error: {response.status_code} - {response.text}")

def text_to_speech_gtts(text, voice_type="Default"):
    lang_map = {
        "Default (gTTS)": "en",
        "British (gTTS)": "en-uk",
        "Australian (gTTS)": "en-au"
    }
    lang = lang_map.get(voice_type, "en")

    tts = gTTS(text=text, lang="en", tld=lang.split("-")[-1] if "-" in lang else "com")
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "narration.mp3")
    tts.save(output_path)
    return output_path

# -----------------------------
# 🚀 APP UI
# -----------------------------

st.title("📖 AI Reddit Story Narrator")
st.caption("Generate multi-paragraph voice-narrated stories using OpenRouter + gTTS")

if st.button("🎬 Generate Story + Narration"):
    if not prompt or not OPENROUTER_API_KEY:
        st.error("⚠️ Please enter both a story prompt and your OpenRouter API key.")
    else:
        with st.spinner("🧠 Generating story..."):
            try:
                story_text = generate_story_with_openrouter(prompt, genre)
                audio_path = text_to_speech_gtts(story_text, voice_option)

                st.markdown("### 📝 Generated Story")
                st.write(story_text)

                st.markdown("### 🔊 Narration")
                with open(audio_path, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                    st.download_button("⬇️ Download MP3", f, file_name="ai_story_narration.mp3")

            except Exception as e:
                st.error(f"❌ Error: {e}")
