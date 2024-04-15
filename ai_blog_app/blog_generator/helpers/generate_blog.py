import os

import assemblyai as aai
import dotenv
import openai
from django.conf import settings
from pytube import YouTube

dotenv.load_dotenv()


def get_youtube_title(link: str) -> str:
    yt = YouTube(link)
    return yt.title


def download_audio(link: str) -> str:
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + ".mp3"
    os.rename(out_file, new_file)
    return new_file


def get_transcript(link: str) -> str:
    audio_file = download_audio(link)
    aai.settings.api_key = os.getenv("AAI_API_KEY")
    transcript = aai.Transcriber().transcribe(audio_file)
    return transcript.text


def generate_blog_from_transcript(transcription: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"""
                Based on the following transcript from a youtube video
                write a comprehensive blog article, write it based on this transcript
                but don't make it look like a youtube video, make it look like a proper article\n\nArticle: \n{transcription}\n\n
                """

    response = openai.completions.create(
        model="davinci-002",
        prompt=prompt,
        max_tokens=1000,
    )

    content = response.choices[0].text.strip()
    return content
