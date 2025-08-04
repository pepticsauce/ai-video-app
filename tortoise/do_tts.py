import argparse
import os
from TTS.api import TTS

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True)
    parser.add_argument("--voice", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    args = parser.parse_args()

    tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tortoise_model", progress_bar=False, gpu=True)
    
    wav = tts.tts(args.text, speaker=args.voice)
    tts.save_wav(wav, args.output_path)

if __name__ == "__main__":
    main()
