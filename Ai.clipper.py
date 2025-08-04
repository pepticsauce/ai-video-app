import os
import random
import yt_dlp
import whisper
from moviepy.editor import VideoFileClip

def download_video(url, path):
    ydl_opts = {'outtmpl': path, 'format': 'bestvideo[ext=mp4]+bestaudio/best'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def transcribe_video(path):
    model = whisper.load_model("base")
    return model.transcribe(path)

def extract_highlights(transcription, min_len, max_len, keywords, num_clips):
    highlights = []
    for segment in transcription['segments']:
        text = segment['text'].lower()
        start = segment['start']
        end = segment['end']
        duration = end - start

        if any(word in text for word in keywords) or len(text.split()) > 8:
            if min_len <= duration <= max_len:
                highlights.append((start, end))

    while len(highlights) < num_clips:
        last_end = transcription['segments'][-1]['end']
        start = random.uniform(0, last_end - max_len)
        end = start + random.uniform(min_len, max_len)
        highlights.append((start, end))

    return highlights[:num_clips]

def create_clips(video_path, highlights, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    clip = VideoFileClip(video_path)
    for i, (start, end) in enumerate(highlights):
        sub = clip.subclip(start, end)

        # Convert to 9:16 vertical format
        w, h = sub.size
        if w > h:
            new_w = h * 9 / 16
            x_center = w / 2
            sub = sub.crop(x_center=x_center, width=new_w)

        output_path = os.path.join(output_folder, f"highlight_{i+1}.mp4")
        sub.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30, verbose=False, logger=None)
    clip.close()
