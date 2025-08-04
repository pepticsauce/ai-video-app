from ai_clipper import download_video, transcribe_video, extract_highlights, create_clips
import streamlit as st
import shutil
import os
from ai_clipper import download_video, transcribe_video, extract_highlights, create_clips

st.title("🎬 AI TikTok Clipper")
st.write("Paste a YouTube or Twitch link. Get 50 AI-generated vertical clips (8–27 sec each).")

url = st.text_input("Enter Video URL")
run = st.button("Generate AI Clips")

if run and url:
    output_dir = "clips"
    zip_file = "ai_clips.zip"
    video_path = "video.mp4"

    with st.spinner("Processing video..."):
        try:
            # Step 1: Download video
            download_video(url, video_path)

            # Step 2: Transcribe
            transcript = transcribe_video(video_path)

            # Step 3: Extract highlights
            highlights = extract_highlights(transcript, 8, 27, [
                "kill", "funny", "insane", "crazy", "clutch", "no way", "help", "wow"
            ], 50)

            # Step 4: Create clips
            create_clips(video_path, highlights, output_dir)

            # Step 5: Zip clips
            shutil.make_archive("ai_clips", 'zip', output_dir)

            # Download link
            with open(zip_file, "rb") as f:
                st.download_button("📥 Download All Clips", f, file_name="ai_clips.zip")

        except Exception as e:
            st.error(f"Error: {e}")
