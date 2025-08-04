import streamlit as st
import requests
import random
import os
import tempfile
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips

# -------------------- CONFIG --------------------
st.set_page_config(page_title="AI Reddit Narrator", layout="centered")
st.title("📖 AI Reddit Narrator (Bark TTS + Minecraft Video)")
st.markdown("Narrates Reddit stories using Bark TTS and overlays Minecraft parkour background.")

# Paste Hugging Face token here OR use secrets
HUGGING_FACE_TOKEN = st.secrets.get("HUGGING_FACE_TOKEN", "hf_your_token_here")

# -------------------- UI --------------------
story_source = st.radio("Choose story source:", ["Reddit (r/stories)", "Paste your own"])
start_button = st.button("🎬 Generate AI Narration Video")

# -------------------- FUNCTIONS --------------------

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
        return None

def generate_bark_audio(full_text):
    chunks = split_text(full_text)
    audio_clips = []
    for i, chunk in enumerate(chunks):
        st.write(f"🔊 Generating audio chunk {i+1}/{len(chunks)}...")
        audio_path = bark_tts(chunk)
        if audio_path:
            audio_clip = AudioFileClip(audio_path)
            audio_clips.append(audio_clip)
        else:
            st.warning(f"Chunk {i+1} failed.")
    final_audio = concatenate_audioclips(audio_clips)
    final_audio_path = os.path.join(tempfile.mkdtemp(), "final_audio.wav")
    final_audio.write_audiofile(final_audio_path)
    return final_audio_path

def merge_with_video(audio_path):
    video_path = "assets/minecraft_clip.mp4"  # Add this file to your repo
    output_path = os.path.join(tempfile.mkdtemp(), "final_video.mp4")

    audio = AudioFileClip(audio_path)
    video = VideoFileClip(video_path).subclip(0, audio.duration)
    final = video.set_audio(audio)
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

# -------------------- MAIN --------------------

if start_button:
    with st.spinner("📥 Getting story..."):
        if story_source == "Reddit (r/stories)":
            story = get_reddit_story()
        else:
            story = st.text_area("Paste your story here:")

    if story:
        st.success("✅ Story ready")
        st.text_area("📝 Story Content", story, height=250)

        with st.spinner("🔊 Generating narration with Bark TTS..."):
            audio_path = generate_bark_audio(story)
            if audio_path:
                st.audio(audio_path)
                with open(audio_path, "rb") as f:
                    st.download_button("⬇️ Download Audio", f, file_name="narration.wav")

        with st.spinner("🎥 Merging with Minecraft background..."):
            try:
                video_path = merge_with_video(audio_path)
                st.video(video_path)
                with open(video_path, "rb") as f:
                    st.download_button("⬇️ Download Final Video", f, file_name="final_story_video.mp4")
            except Exception as e:
                st.error("⚠️ Video merge failed. Make sure `assets/minecraft_clip.mp4` exists.")
    else:
        st.warning("No story available.")
