import streamlit as st
import requests
import tempfile
import os
import pyttsx3
import random
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip

st.set_page_config(page_title="AI Reddit Narrator Lite", layout="centered")

st.title("📖 AI Reddit Narrator (Lite)")
st.markdown("Narrates Reddit stories using lightweight tools for Streamlit Cloud.")

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
        return "Failed to load story."

def generate_tts_pyttsx3(text):
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "narration.mp3")
    
    engine = pyttsx3.init()
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    return output_path

def merge_with_background(audio_path):
    temp_dir = tempfile.mkdtemp()
    video_path = "assets/minecraft_clip.mp4"  # You upload this file
    final_output = os.path.join(temp_dir, "output.mp4")

    audio = AudioFileClip(audio_path)
    video = VideoFileClip(video_path).subclip(0, audio.duration)
    final = video.set_audio(audio)
    final.write_videofile(final_output, codec="libx264", audio_codec="aac")
    
    return final_output

if start_button:
    with st.spinner("📥 Getting story..."):
        if story_source == "Reddit (r/stories)":
            story = get_reddit_story()
        else:
            story = st.text_area("Paste your story here:")

    if story:
        st.text_area("Story:", story, height=200)

        with st.spinner("🔊 Generating narration..."):
            audio_path = generate_tts_pyttsx3(story)
            st.audio(audio_path)
            with open(audio_path, "rb") as f:
                st.download_button("⬇️ Download Audio", f, "narration.mp3")

        with st.spinner("🎥 Merging with Minecraft video..."):
            try:
                video_output = merge_with_background(audio_path)
                st.video(video_output)
                with open(video_output, "rb") as f:
                    st.download_button("⬇️ Download Final Video", f, "final_video.mp4")
            except Exception as e:
                st.error("Video merge failed. Make sure video exists in /assets.")
    else:
        st.warning("No story provided.")
