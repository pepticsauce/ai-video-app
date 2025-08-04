import streamlit as st
import openai
import requests
import tempfile
import os
from PIL import Image
from io import BytesIO
from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
    AudioFileClip,
    CompositeVideoClip
)
import textwrap
from elevenlabs import generate, save, set_api_key

# Set up Streamlit input fields for API keys
openai_api_key = st.text_input("OpenAI API Key", type="password")
elevenlabs_api_key = st.text_input("ElevenLabs API Key", type="password")

VOICE_ID = "Rachel"  # Change this to your preferred ElevenLabs voice

# ✅ Updated OpenAI v1.x client initialization
client = openai.OpenAI(api_key=openai_api_key)

def generate_script(prompt):
    response = client.chat.completions.create(
        model='gpt-4',
        messages=[
            {"role": "system", "content": "Write a short engaging video script for a narrator, 1 to 2.5 minutes long."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def get_image_from_dalle(prompt, size='512x512'):
    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size=size,
        n=1
    )
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    return Image.open(BytesIO(img_data))

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
    duration = max(5, int(150 / len(image_prompts)))
    for i, prompt in enumerate(image_prompts):
        img = get_image_from_dalle(prompt)
        path = f'image_{i}.png'
        img.save(path)
        clip = ImageClip(path).set_duration(duration).resize(width=720)
        clips.append(clip)
    video = concatenate_videoclips(clips)
    audio_file = text_to_speech_elevenlabs(script_text)
    audio_clip = AudioFileClip(audio_file).set_duration(video.duration)
    final = video.set_audio(audio_clip)
    temp_dir = tempfile.mkdtemp()
    out_path = os.path.join(temp_dir, "output_video.mp4")
    final.write_videofile(out_path, fps=24)
    return out_path

# Streamlit app UI
st.title("🎬 AI Video Generator (Private)")

if openai_api_key and elevenlabs_api_key:
    prompt = st.text_area("Enter your video prompt:", height=100)
    if st.button("Generate Video"):
        with st.spinner("Creating your video..."):
            try:
                script = generate_script(prompt)
                img_prompts = textwrap.wrap(prompt, width=40)[:5]
                video_file = make_video(script, img_prompts)
                st.success("✅ Your video is ready!")
                with open(video_file, "rb") as f:
                    st.video(f.read())
                    st.download_button("⬇️ Download Video", f, file_name="ai_video.mp4")
            except Exception as e:
                st.error(f"❌ Error: {e}")
else:
    st.warning("🔑 Please enter your OpenAI and ElevenLabs API keys to continue.")
