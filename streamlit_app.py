import streamlit as st
import openai
import textwrap
from moviepy.editor import *
from PIL import Image
import requests
from io import BytesIO
from elevenlabs import generate, save, set_api_key
import tempfile
import os

st.set_page_config(page_title="Private AI Video Generator", layout="centered")

openai_api_key = st.text_input("Enter OpenAI API Key", type="password")
elevenlabs_api_key = st.text_input("Enter ElevenLabs API Key", type="password")
VOICE_ID = 'Rachel'
