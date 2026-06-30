# Realtime Transcriber and Translator

[![Support me on Patreon](https://img.shields.io/badge/Patreon-Support%20my%20work-FF424D?style=flat&logo=patreon&logoColor=white)](https://www.patreon.com/AndersBjarby)

A near-realtime speech transcription and translation pipeline built from three small scripts that hand off through watched folders. It continuously records short audio clips from your microphone, transcribes them (Swedish, via Groq's Whisper), and translates the running text into a target language of your choice (via OpenAI).

## How it works

The three components run independently and communicate through the filesystem:

1. **`recorder.py`** — records the microphone in rolling ~3-second chunks using two alternating threads and writes timestamped `.wav` files into `audio_clips/`.
2. **`transcriber.py`** — watches `audio_clips/` for new `.wav` files and transcribes each one with `whisper-large-v3` on the Groq API (configured for Swedish), writing `.txt` files into `transcriptions/`.
3. **`translator.py`** — watches `transcriptions/` for new `.txt` files and translates the accumulated text into a target language with `gpt-4o-mini`, keeping a rolling message history for naturally flowing output and printing the latest translation to a cleared terminal. Results are saved into `translations/`.

## Requirements

- Python packages: `pyaudio`, `watchdog`, `openai`, `python-dotenv`
- A `.env` file with `GROQ_API_KEY` (for transcription) and `OPENAI_API_KEY` (for translation)

## Setup

```bash
pip install pyaudio watchdog openai python-dotenv

# .env
echo "GROQ_API_KEY=..." >> .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

## Usage

Run each script in its own terminal:

```bash
python recorder.py
python transcriber.py
python translator.py English      # pass the target language as an argument
```

## Tech

Python, PyAudio, watchdog (folder watching), Groq Whisper (`whisper-large-v3`), OpenAI `gpt-4o-mini`.
