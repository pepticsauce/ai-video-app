import streamlit as st
import requests
import tempfile
import os
import random
import subprocess
from bs4 import BeautifulSoup
from moviepy.editor import *
import yt_dlp

# -------------------- CONFIG --------------------
st.set_page_config(page_title="AI Reddit Narrator", layout="centered")

# -------------------- UI --------------------
st.title("📖 AI Reddit Story Narrator")
st.markdown("Narrates a Reddit story with AI and overlays Minecraft parkour video.")

story_source = st.radio("Choose story source:", ["Reddit (r/stories)", "Paste your own"])
voice = st.selectbox("Choose voice (Tortoise TTS):", ["daniel", "emma", "pat", "jenny", "random"])
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
        return "Error: Unable to fetch Reddit story."

def generate_tts(text, voice="daniel"):
    temp_dir = tempfile.mkdtemp()
    tts_path = os.path.join(temp_dir, "narration.wav")
    
    if voice == "random":
        voice = random.choice(["daniel", "emma", "pat", "jenny"])
    
    cmd = [
        "python3", "tortoise/do_tts.py",
        "--text", text,
        "--voice", voice,
        "--output_path", tts_path
    ]
    subprocess.run(cmd, check=True)
    return tts_path

def download_background_video(youtube_url, max_duration=120):
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "bg_video.mp4")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': output_path,
        'quiet': True,
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    clip = VideoFileClip(output_path)
    if clip.duration > max_duration:
        clip = clip.subclip(0, max_duration)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    return output_path

def generate_video(audio_path):
    temp_dir = tempfile.mkdtemp()
    yt_url = "https://www.youtube.com/watch?v=9A6FsOl3bdM"  # Sample parkour video
    background_path = download_background_video(yt_url)
    output_path = os.path.join(temp_dir, "final_video.mp4")

    audio = AudioFileClip(audio_path)
    video = VideoFileClip(background_path).subclip(0, audio.duration)
    final = video.set_audio(audio)

    final.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

# -------------------- MAIN APP --------------------

if start_button:
    with st.spinner("📥 Fetching story..."):
        if story_source == "Reddit (r/stories)":
            story = get_reddit_story()
        else:
            story = st.text_area("Paste your story here:")

    if story:
        st.success("✅ Story ready!")
        st.text_area("📝 Story Content", story, height=200)

        with st.spinner("🔊 Generating narration..."):
            try:
                audio_path = generate_tts(story, voice)
                st.audio(audio_path)
                with open(audio_path, "rb") as f:
                    st.download_button("⬇️ Download Narration Audio", f, file_name="narration.wav")
            except Exception as e:
                st.error("TTS generation failed.")
                st.stop()

        with st.spinner("🎥 Rendering video..."):
            try:
                video_path = generate_video(audio_path)
                st.video(video_path)
                st.caption("🎬 Background from [Minecraft Parkour YouTube video](https://www.youtube.com/watch?v=9A6FsOl3bdM)")

                with open(video_path, "rb") as f:
                    st.download_button("⬇️ Download Final Video", f, file_name="final_story_video.mp4")
            except Exception as e:
                st.error("Video rendering failed.")
    else:
        st.warning("❗ No story available.")
