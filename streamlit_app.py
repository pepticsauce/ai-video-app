import streamlit as st
from gtts import gTTS
import tempfile
import os

st.title("🎤 Free AI Reddit Narrator")

# User prompt input
user_input = st.text_area("Enter your Reddit-style story here:", height=200)

# Optional genre filter (for future extension)
genre = st.selectbox("Select a Genre (optional):", ["None", "Horror", "Romance", "Funny", "Mystery"])

if st.button("🧠 Generate Narration"):
    if not user_input.strip():
        st.error("Please enter a story.")
    else:
        with st.spinner("Generating voice..."):
            # Format story based on genre
            story_text = f"[Genre: {genre}] {user_input}" if genre != "None" else user_input

            # Convert to speech
            tts = gTTS(text=story_text, lang="en")
            temp_dir = tempfile.mkdtemp()
            audio_path = os.path.join(temp_dir, "narration.mp3")
            tts.save(audio_path)

            # Play + download
            with open(audio_path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
                st.download_button("⬇️ Download MP3", f, file_name="story_narration.mp3")
