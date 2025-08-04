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
    CompositeVideoClip,
    TextClip
)
import textwrap
from elevenlabs import generate, save, set_api_key

# Optional: Store your keys here (or input in app)
openai_api_key = st.text_input("OpenAI API Key", type="password")
elevenlabs_api_key = st.text_input("ElevenLabs API Key", type="password")

# Optional: Use a specific ElevenLabs voice
VOICE_ID = "Rachel"  # Or another ElevenLabs voice name

def generate_script(prompt):
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[
            {"role": "system", "content": "Write a short engaging video script for a narrator, 1 to 2.5 minutes long."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def get_image_from_dalle(prompt, size='512x512'):
    openai.api_key = openai_api_key
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=size
    )
    image_url = response['data'][0]['url']
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

def create_subtitle_clips(script_text, total_duration):
    sentences = textwrap.wrap(script_text, width=80)
    per_sentence_duration = total_duration / len(sentences)
    clips = []
    current_time = 0
    for sentence in sentences:
        clip = TextClip(sentence, fontsize=28, color='white', bg_color='black', font='Arial')
        clip = clip.set_position(('center', 'bottom')).set_duration(per_sentence_duration).set_start(current_time)
        clips.append(clip)
        current_time += per_sentence_duration
    return clips

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
    subtitles = create_subtitle_clips(script_text, video.duration)
    final = CompositeVideoClip([video] + subtitles).set_audio(audio_clip)
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
