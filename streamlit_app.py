import streamlit as st
import requests
import random
import os
import tempfile

# Streamlit setup
st.set_page_config(page_title="AI Reddit Narrator", layout="centered")
st.title("📖 AI Reddit Narrator")
st.markdown("Narrated Reddit story + Minecraft parkour background (via YouTube)")

# Hugging Face token (from Streamlit Secrets or hardcoded)
HUGGING_FACE_TOKEN = st.secrets.get("HUGGING_FACE_TOKEN", "hf_your_token_here")

# Story source
story_source = st.radio("Choose story source:", ["Reddit (r/stories)", "Paste your own"])
custom_story = None
if story_source == "Paste your own":
    custom_story = st.text_area("Paste your story here:", height=200)

start_button = st.button("🎬 Generate Narration")

# ------------ Reddit Fetch (Pushshift) -------------
def get_reddit_story():
    try:
        url = "https://api.pushshift.io/reddit/search/submission/?subreddit=stories&sort=desc&size=20"
        res = requests.get(url)
        posts = res.json().get("data", [])
        for post in posts:
            title = post.get("title", "")
            body = post.get("selftext", "")
            if len(body.strip()) > 100:
                return f"{title}\n\n{body}"
        return "No suitable stories found."
    except Exception as e:
        return f"Error fetching from Pushshift: {e}"

# ------------ Text Chunking -------------
def split_text(text, max_len=500):
    sentences = text.split('. ')
    chunks, current = [], ""
    for sentence in sentences:
        if len(current + sentence) <= max_len:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "
    if current:
        chunks.append(current.strip())
    return chunks

# ------------ Bark TTS -------------
def bark_tts(text_chunk):
    API_URL = "https://api-inference.huggingface.co/models/suno/bark"
    headers = {
        "Authorization": f"Bearer {HUGGING_FACE_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(API_URL, headers=headers, json={"inputs": text_chunk})
    if response.status_code == 200:
        temp_dir = tempfile.mkdtemp()
        out_path = os.path.join(temp_dir, "chunk.wav")
        with open(out_path, "wb") as f:
            f.write(response.content)
        return out_path
    else:
        st.error(f"Bark TTS failed: {response.status_code}")
        return None

# ------------ Narration Generator -------------
def generate_bark_audio(full_text):
    chunks = split_text(full_text)
    audio_paths = []
    for i, chunk in enumerate(chunks):
        st.write(f"🔊 Generating chunk {i+1}/{len(chunks)}...")
        audio_path = bark_tts(chunk)
        if audio_path:
            audio_paths.append(audio_path)
        else:
            st.warning(f"Chunk {i+1} failed.")
    return audio_paths[0] if audio_paths else None

# ------------ Main Flow -------------
if start_button:
    with st.spinner("📥 Fetching story..."):
        story = custom_story if story_source == "Paste your own" else get_reddit_story()

    if story and "Error" not in story:
        st.success("✅ Story loaded")
        st.text_area("📝 Story Content", story, height=300)

        with st.spinner("🔊 Generating narration..."):
            audio_path = generate_bark_audio(story)

        if audio_path:
            st.audio(audio_path)
            with open(audio_path, "rb") as f:
                st.download_button("⬇️ Download Narration", f, file_name="narration.wav")

        st.markdown("### 🎮 Minecraft Parkour Video")
        st.video("https://www.youtube.com/watch?v=9A6FsOl3bdM")

    else:
        st.warning("No story found or provided.")
