import streamlit as st
import tempfile
import os
import subprocess
from TTS.api import TTS

# Initialize TTS model
@st.cache_resource
def load_tts_model():
    return TTS(model_name="tts_models/en/multi-dataset/tortoise-v2", progress_bar=False, gpu=False)

tts = load_tts_model()

# Streamlit UI
st.title("🎙️ AI Story Narrator with Tortoise TTS")
st.markdown("Generate realistic voice narration from your own prompts.")

# Genre selection
genre = st.selectbox("Choose a story genre:", ["Random", "Horror", "Romance", "Adventure", "Mystery", "Sci-Fi"])
user_prompt = st.text_area("Enter your story prompt or idea here:")

# Voice selection
voice = st.selectbox("Choose a voice:", ["tom", "deniro", "pat", "jessica", "william", "lj", "emma"])
generate_button = st.button("🎤 Generate Narration")

def generate_story_text(prompt, genre):
    # Simple text generation without external APIs (replace with OpenRouter or local LLM if desired)
    base = f"Here's a {genre.lower()} story: {prompt}\n\n"
    paragraphs = [
        "It all began on a day like any other, yet something felt different.",
        "As the hours passed, unexpected events unfolded that would change everything.",
        "The character faced a challenge they never anticipated, pushing them to their limits.",
        "In the end, nothing was quite the same — but some things were finally understood.",
    ]
    return base + "\n\n".join(paragraphs)

def convert_wav_to_mp3(wav_path, mp3_path):
    subprocess.run([
        "ffmpeg", "-y", "-i", wav_path, "-vn", "-ar", "44100", "-ac", "2", "-b:a", "192k", mp3_path
    ], check=True)

if generate_button and user_prompt:
    with st.spinner("Generating story and audio..."):
        story_text = generate_story_text(user_prompt, genre)
        
        # Generate audio using Tortoise
        temp_dir = tempfile.mkdtemp()
        wav_path = os.path.join(temp_dir, "story.wav")
        mp3_path = os.path.join(temp_dir, "story.mp3")
        
        tts.tts_to_file(text=story_text, file_path=wav_path, speaker=voice)
        convert_wav_to_mp3(wav_path, mp3_path)

        # Display result
        st.success("Narration complete!")
        st.markdown("### 📝 Story Preview")
        st.text(story_text)

        st.audio(mp3_path, format="audio/mp3")
        with open(mp3_path, "rb") as f:
            st.download_button("⬇️ Download MP3", f, file_name="narrated_story.mp3")
