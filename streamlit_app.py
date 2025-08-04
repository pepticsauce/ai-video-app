import streamlit as st
import requests
import tempfile
import os
from PIL import Image
from io import BytesIO
from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
    AudioFileClip
)
import textwrap
from elevenlabs import generate, save, set_api_key

# 🔐 API key inputs
huggingface_api_key = st.text_input("Hugging Face API Key", type="password")
elevenlabs_api_key = st.text_input("ElevenLabs API Key", type="password")

VOICE_ID = "Rachel"  # You can change this to another ElevenLabs voice if desired

# 🎬 Streamlit UI
st.title("🎬 Free AI Video Generator (No OpenAI Needed)")

if huggingface_api_key and elevenlabs_api_key:
    prompt = st.text_area("Enter your video topic or idea:", height=100)

    if st.button("Generate Video"):
        with st.spinner("Generating video..."):
            try:
                # Step 1: Generate script
                script = generate_script(prompt)

                # Step 2: Generate images from key phrases in prompt
                img_prompts = textwrap.wrap(prompt, width=40)[:5]

                # Step 3: Create video
                video_path = make_video(script, img_prompts)

                # Step 4: Show video and download
                st.success("✅ Your video is ready!")
                with open(video_path, "rb") as f:
                    st.video(f.read())
                    st.download_button("⬇️ Download Video", f, file_name="ai_video.mp4")

            except Exception as e:
                st.error(f"❌ Error: {e}")
else:
    st.warning("🔐 Please enter both your Hugging Face and ElevenLabs API keys to continue.")

# ------------------------------
# 🔧 Functions
# ------------------------------

def generate_script(prompt):
    HF_API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    headers = {"Authorization": f"Bearer {huggingface_api_key}"}
    payload = {
        "inputs": f"Write a 1 to 2.5 minute narrator script based on this prompt:\n\n{prompt}",
        "parameters": {"max_new_tokens": 300}
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result[0]["generated_text"]
    else:
        raise Exception(f"Hugging Face Error: {response.text}")

def get_image_from_dalle(prompt):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {
        "Authorization": f"Bearer {huggingface_api_key}",
        "Accept": "image/png"
    }
    response = requests.post(url, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        raise Exception(f"Image generation failed: {response.text}")

def text_to_speech_elevenlabs(text, filename='voice.mp3'):
    set_api_key(elevenlabs_api_key)
    audio = generate(
        text=text,
        voice=VOICE_ID,
        model='eleven_multilingual_v2'
    )
    save(audio, filename)
    return filename

def make_video(script_text, image_prompts):
    clips = []
    duration = max(5, int(150 / len(image_prompts)))  # ~150s max total video length
    for i, prompt in enumerate(image_prompts):
        img = get_image_from_dalle(prompt)
        path = f'image_{i}.png'
        img.save(path)
        clip = ImageClip(path).set_duration(duration).resize(width=720)
        clips.append(clip)

    video = concatenate_videoclips(clips)

    # Narration audio
    audio_file = text_to_speech_elevenlabs(script_text)
    audio_clip = AudioFileClip(audio_file).set_duration(video.duration)

    # Combine
    final = video.set_audio(audio_clip)
    temp_dir = tempfile.mkdtemp()
    out_path = os.path.join(temp_dir, "output_video.mp4")
    final.write_videofile(out_path, fps=24)
    return out_path
