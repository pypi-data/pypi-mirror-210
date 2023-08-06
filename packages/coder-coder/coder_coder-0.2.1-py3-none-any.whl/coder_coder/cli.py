from __future__ import print_function
import os
import time
from pathlib import Path
from typing import Optional

import typer
import mac_say

import openai
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "env" /".env")
openai.api_key = os.environ["OPENAI_API_KEY"]  # supply your API key however you choose
openai.organization = os.environ["OPENAI_ORG_ID"]  # supply your organization key however you choose


app = typer.Typer()


@app.callback()
def callback():
    """
    Awesome Portal Gun
    """


@app.command()
def code(user_prompt: str = typer.Argument(...),
         out_file: Optional[str] = typer.Option(None),
         in_file: Optional[str] = typer.Option(None)):
    """
    code
    """
    typer.echo(f"Coding: {user_prompt}")
    if in_file:
        with open(in_file, "r") as f:
            existing_code = f.read()
        prompt = f"""Given this existing code {existing_code}. Write code to {user_prompt}. 
        Use or rewrite the existing code in a logical way without losing any of the functionality of the existing code.
         Output code only. No description."""
    else:
        prompt = f"Write code to {user_prompt}. Output the code only. No description."
    completion = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
    text_response = completion.choices[0].message.content
    typer.echo(text_response)
    if out_file:
        with open(out_file, "w") as f:
            f.write(text_response)


@app.command()
def plan(user_prompt: str = typer.Argument(...),
         out_file: Optional[str] = typer.Option(None)):
    prompt = f"""
Develop a plan for the following goal: {user_prompt}
"""
    completion = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
    text_response = completion.choices[0].message.content
    typer.echo(text_response)
    if out_file:
        with open(out_file, "w") as f:
            f.write(text_response)


@app.command()
def prompt(user_prompt: str = typer.Argument(...),
         out_file: Optional[str] = typer.Option(None)):
    completion = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": user_prompt}])
    text_response = completion.choices[0].message.content
    typer.echo(text_response)
    if out_file:
        with open(out_file, "w") as f:
            f.write(text_response)


import openai
import wave
import pyaudio


api_url = "https://api.openai.com/v1/asr/whisper/transcripts"

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 15
WAVE_OUTPUT_FILENAME = "output.wav"


def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))
    wf.close()

def get_text_from_audio():
    with open(WAVE_OUTPUT_FILENAME, 'rb') as file:

        transcript = openai.Audio.transcribe("whisper-1", file)
    return transcript.get("text", "")


def improve_text(text, params=None):
    if params is None:
        params = {}
    mode = params.get("mode", "improve")
    if mode == "improve":
        prompt = f"""Improve the following text: {text}. Use a {params.get('tone', 'formal')} tone."""
    if mode == "prompt":
        prompt = f"""Write a text based on this prompt: {text}. Use a {params.get('tone', 'formal')} tone."""
    completion = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
    text_response = completion.choices[0].message.content
    return text_response


import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']


# The ID of a sample document.
DOCUMENT_ID = '1b-19zBn1cpyMJyY8WYt6kE40qo4bnGGq8iqK20oylC0'


def main():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../env/client_secret_741769037270-hfikkagrv0hm00p723ullv6h4c0dnr8a.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('docs', 'v1', credentials=creds)

        # Retrieve the documents contents from the Docs service.
        document = service.documents().get(documentId=DOCUMENT_ID).execute()
        doc = Document(document)
        doc.get_coder_coder_header()
        params = doc.get_params()
        text = improve_text(doc.user_text, params)
        print(text)
        start, end = doc.get_ai_start_end()
        requests = []
        if start < end:
            requests.append({
                'deleteContentRange': {
                    'range': {
                        'startIndex': start,
                        'endIndex': end - 2,
                    }

                }
            })

        requests.append({
                'insertText': {
                    'location': {
                        'index': start - 1,
                    },
                    'text': f"\n\n{text}"
                }
            }
        )

        result = service.documents().batchUpdate(
            documentId=DOCUMENT_ID, body={'requests': requests}).execute()

        print('The title of the document is: {}'.format(document.get('title')))
    except HttpError as err:
        print(err)


class Document:
    def __init__(self, document):
        self.document = document

        self.ai_header_position = (None, None)
        self.ai_header = None

    def get_coder_coder_header(self):
        self.user_text = ""
        for c, content in enumerate(self.document.get('body').get('content', [])):
            paragraph = content.get('paragraph')
            if paragraph is None:
                continue
            for e, element in enumerate(paragraph.get('elements', [])):
                text_run = element.get('textRun')
                if text_run is None:
                    continue
                text = text_run.get('content')
                if text.startswith('[[coder-coder]'):
                    self.ai_header_position = (c, e)
                    self.ai_header = text.strip()
                    return
                else:
                    self.user_text += text.strip()

    def get_ai_start_end(self):
        content = self.document.get('body').get('content', [])
        end_ai_content = content[-1]["endIndex"]
        start_ai_content = content[self.ai_header_position[0]]["endIndex"]

        return start_ai_content, end_ai_content

    def get_params(self):
        header = self.ai_header.replace("[[coder-coder]", "")
        header = header.strip()
        header = header[:-1]
        params = header.split(" ")
        params = {param.split("=")[0]: param.split("=")[1] for param in params}
        return params


# main()

# while True:
#     record_audio()
#     user_prompt = get_text_from_audio()
#     prompt = f"""You are a superhelpful friend that helps people with their problems. You are helping your friend with a problem. Your friend says: {user_prompt}.
#     Reply with a solution to your friend's problem. Make your response conversational such that your friend will respond back to you.
#     """
#     completion = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
#     text_response = completion.choices[0].message.content
#
#     mac_say.say(text_response)
#     time.sleep(2)


