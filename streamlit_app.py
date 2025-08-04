import streamlit as st
import requests
import random
import os
import tempfile

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Reddit Narrator (No Video Merge)", layout="centered")
st.title("📖 AI Reddit Narrator (Bark TTS, No Video Merge)")
st.markdown("Reddit story narration + Minecraft parkour YouTube background (separate)")

# Paste your Hugging Face token here or use secrets
HUGGING_FACE_TOKEN = st.secrets.get("HUGGING_FACE_TOKEN", "hf_your_token_here")

story_source = st.radio("Choose story source:", ["Reddit (r/stories)", "Paste your own"])
start_button = st.button("🎬 Generate Narration")

def get_reddit_story():
    url = "https://www.reddit.com/r/stories/top/.json?t=day&limit=10"
    headers = {'User-agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers)
        posts = res.json()["data"]["children"]
        post = random.choice(posts)
        title = post["data"]["title"]
        selftext = post["data"]["selftext"]
        return f"{title}\n\n{selftext}"
    except:
        return "Failed to fetch story."

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

def generate_bark_audio(full_text):
    chunks = split_text(full_text)
    audio_paths = []
    for i, chunk in enumerate(chunks):
        st.write(f"🔊 Generating audio chunk {i+1}/{len(chunks)}...")
        audio_path = bark_tts(chunk)
        if audio_path:
            audio_paths.append(audio_path)
        else:
            st.warning(f"Chunk {i+1} failed.")
    # If multiple chunks, just return first for simplicity (no merge)
    return audio_paths[0] if audio_paths else None

if start_button:
    with st.spinner("📥 Fetching story..."):
        if story_source == "Reddit (r/stories)":
            story = get_reddit_story()
        else:
            story = st.text_area("Paste your story here:")

    if story:
        st.success("✅ Story ready")
        st.text_area("📝 Story Content", story, height=250)

        with st.spinner("🔊 Generating Bark narration..."):
            audio_path = generate_bark_audio(story)
            if audio_path:
                st.audio(audio_path)
                with open(audio_path, "rb") as f:
                    st.download_button("⬇️ Download Narration Audio", f, file_name="narration.wav")

        st.markdown("### 🎮 Minecraft Parkour Background Video")
        st.video("https://www.youtube.com/watch?v=9A6FsOl3bdM")
    else:
        st.warning("No story provided.")
